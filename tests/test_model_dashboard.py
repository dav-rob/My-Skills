import datetime
import http.client
import importlib.util
import json
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SERVER_PY = REPO / "dashboard" / "server.py"
TEMPLATE = REPO / "dashboard" / "index.html"
SKILL_REL = Path("skills/model-use/SKILL.md")
MODELS_REL = Path("skills/model-use/references/models.md")

# Stable examples exercise rendering without coupling tests to weekly choices.
# The CLI test below separately exercises the real repository sources.
SKILL_FIXTURE = """# Model use
Keep the model the user is talking to as project manager. It verifies the work.

## Round robin
| Project manager | Worker order, then repeat |
| --- | --- |
| Codex / OpenAI | Sonnet → Hydrogen |
| Claude / Anthropic | Sol → Hydrogen |
| Gemini / Google | Sol → Sonnet |

Sonnet is one slot with two routes. Hydrogen gets ordinary work, not just failovers.

## Assign and verify
Require the CLI's successful terminal result and verify the work.

## Fail over once
Make at most one pass through the eligible routes per task.

If all eligible workers are unavailable, the manager does the work directly.
"""

MODELS_FIXTURE = """# Current workhorses
Assessed: 2026-11-18. These are test examples, not live recommendations. Recheck discovery before running.

| Family / role | Preferred route and exact model | Effort | Route fallback |
| --- | --- | --- | --- |
| Sol worker | `codex`: `gpt-6.1-sol` | `high` | Other worker |
| Sonnet worker | `claude`: `claude-sonnet-5-5` | `high` | `agy`: `claude-sonnet-5-5-high` |
| Hydrogen worker | `agy`: `gemini-4-hydrogen-high` | `high` | Other worker |
| Weekly assessor | `codex`: `gpt-6.1-sol` | `xhigh` | Preserve table |

## Published scores
Example fixture benchmarks only, unrelated to live choices.

### Synthetic coding suite
| Example model | Score |
| --- | --- |
| Fixture-Alpha | 71.2% |
| Fixture-Beta | 68.4% |

### Synthetic cost table
- Cost figures below are placeholder examples.

| Example model | Cost per task |
| --- | --- |
| Fixture-Alpha | $0.14 |
| Fixture-Beta | $0.09 |

## Selection reasons
Reasons below are synthetic test fixtures.

### Slot rationale
- Fixture-Alpha handles broad implementation fixtures.
- Fixture-Beta covers alternate fixture verification.

## Local evidence
Smoke response: MODEL_USE_OK. App competence is separate.

## Assessment sources
[Artificial Analysis coding agents](https://artificialanalysis.ai/agents/coding-agents)
"""

_spec = importlib.util.spec_from_file_location("model_dashboard_server", SERVER_PY)
dash = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dash)


class DashboardCase(unittest.TestCase):
    """Starts an ephemeral server against isolated, stable example sources."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="model-dashboard-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        for rel, source in ((SKILL_REL, SKILL_FIXTURE), (MODELS_REL, MODELS_FIXTURE)):
            target = self.tmp / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source, encoding="utf-8")
        self.server = dash.make_server(0, repo_root=self.tmp)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown()
        self.thread.join(timeout=5)
        self.server.server_close()

    # helpers ---------------------------------------------------------------
    def request(self, method="GET", path="/", host=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            hdrs = {"Host": host if host is not None else f"127.0.0.1:{self.port}"}
            hdrs.update(headers or {})
            conn.request(method, path, headers=hdrs)
            resp = conn.getresponse()
            body = resp.read().decode("utf-8", "replace")
            return resp, body
        finally:
            conn.close()

    def edit(self, rel, fn):
        path = self.tmp / rel
        path.write_text(fn(path.read_text(encoding="utf-8")), encoding="utf-8")


class HealthyRenderingTests(DashboardCase):
    def test_home_page_content(self):
        resp, body = self.request()
        self.assertEqual(resp.status, 200)
        self.assertTrue(resp.getheader("Content-Type").startswith("text/html"))
        self.assertIn("2026-11-18", body)
        self.assertIn("Last assessed", body)
        self.assertIn("not a benchmark win", body)
        for needle in (
            "gpt-6.1-sol",
            "claude-sonnet-5-5-high",
            "gemini-4-hydrogen-high",
            "Weekly assessor",
            "Codex / OpenAI",
            "Sonnet → Hydrogen",
            "Sol → Sonnet",
            "Monday at 09:00 London",
            "Allowance is not measured",
            "Local and private",
            "Read-only",
            "Local evidence",
            "Artificial Analysis coding agents",
            "MODEL_USE_OK",
        ):
            self.assertIn(needle, body, needle)
        self.assertIn('href="https://artificialanalysis.ai/agents/coding-agents"', body)
        self.assertIn("<details", body)
        self.assertNotIn("%%", body)  # every template token was filled

    def test_page_has_no_script_or_external_assets(self):
        _, body = self.request()
        self.assertNotIn("<script", body.lower())
        for attr in ('src="http', "src='http", 'rel="stylesheet"', "@import", "url(http"):
            self.assertNotIn(attr, body)

    def test_index_html_alias_and_query_string(self):
        for path in ("/index.html", "/?refresh=1"):
            resp, body = self.request(path=path)
            self.assertEqual(resp.status, 200, path)
            self.assertIn("Current recommendations", body)

    def test_head_has_headers_without_body(self):
        resp, body = self.request("HEAD")
        self.assertEqual(resp.status, 200)
        self.assertEqual(body, "")
        self.assertGreater(int(resp.getheader("Content-Length")), 1000)

    def test_healthz_ok(self):
        resp, body = self.request(path="/healthz")
        self.assertEqual(resp.status, 200)
        self.assertEqual(json.loads(body), {"status": "ok"})
        self.assertEqual(resp.getheader("Content-Type"), "application/json")

    def test_assessment_age_does_not_claim_maintenance_failed(self):
        fresh = dash.render_page(self.tmp, today=datetime.date(2026, 11, 20))
        self.assertIn("Assessed 2 days ago", fresh)
        self.assertNotIn("may be overdue", fresh)
        stale = dash.render_page(self.tmp, today=datetime.date(2026, 12, 1))
        self.assertIn("Assessed 13 days ago", stale)
        self.assertNotIn("overdue", stale)

    def test_no_model_ids_duplicated_in_code_or_template(self):
        for path in (SERVER_PY, TEMPLATE):
            text = path.read_text(encoding="utf-8")
            for model_id in ("gpt-6.1-sol", "claude-sonnet-5-5", "gemini-4-hydrogen"):
                self.assertNotIn(model_id, text, f"{model_id} in {path.name}")

    def test_template_tokens_not_substituted_inside_markdown(self):
        self.edit(
            MODELS_REL,
            lambda t: t.replace("Recheck discovery", "Braces {x} and %%ROTATION_TABLE%% and Recheck discovery"),
        )
        _, body = self.request()
        self.assertIn("Braces {x} and %%ROTATION_TABLE%% and Recheck discovery", body)

    def test_published_scores_and_selection_reasons_in_recommendations_order(self):
        resp, body = self.request()
        self.assertEqual(resp.status, 200)
        recs_start = body.index('id="h-recs"')
        allowance_start = body.index('id="h-allowance"')
        recs_html = body[recs_start:allowance_start]
        self.assertNotIn("<details", recs_html)
        markers = [
            "gpt-6.1-sol",
            "<h3>Published scores</h3>",
            "Example fixture benchmarks only",
            "<h4>Synthetic coding suite</h4>",
            'aria-label="Synthetic coding suite"',
            "71.2%",
            "<h4>Synthetic cost table</h4>",
            "Cost figures below are placeholder examples.",
            'aria-label="Synthetic cost table"',
            "$0.14",
            "<h3>Selection reasons</h3>",
            "Reasons below are synthetic test fixtures.",
            "<h4>Slot rationale</h4>",
            "Fixture-Alpha handles broad implementation fixtures.",
        ]
        positions = [recs_html.index(m) for m in markers]
        self.assertEqual(positions, sorted(positions))

    def test_behaviour_subtitle_explains_rotation_resumption_and_fallback(self):
        _, body = self.request()
        beh_start = body.index('id="h-behaviour"')
        recs_start = body.index('id="h-recs"')
        beh_html = body[beh_start:recs_start]
        sub_start = beh_html.index('<p class="sub">')
        sub_end = beh_html.index("</p>", sub_start)
        subtitle = beh_html[sub_start:sub_end].lower()
        self.assertIn("new tasks", subtitle)
        self.assertIn("alternate", subtitle)
        self.assertIn("repeat", subtitle)
        self.assertIn("resumptions", subtitle)
        self.assertIn("fallback", subtitle)
        self.assertNotIn("failover", subtitle)
        self.assertNotIn("fail over", subtitle)


class LiveUpdateTests(DashboardCase):
    def test_model_edit_appears_without_restart(self):
        _, before = self.request()
        self.assertIn("gpt-6.1-sol", before)
        self.edit(MODELS_REL, lambda t: t.replace("gpt-6.1-sol", "gpt-live-edit-9"))
        _, after = self.request()
        self.assertIn("gpt-live-edit-9", after)
        self.assertNotIn("gpt-6.1-sol", after)

    def test_assessed_date_and_rotation_edit_appear(self):
        self.edit(MODELS_REL, lambda t: t.replace("Assessed: 2026-11-18", "Assessed: 2027-02-03"))
        self.edit(SKILL_REL, lambda t: t.replace("| Sol → Sonnet |", "| Sol → Zebra |"))
        _, body = self.request()
        self.assertIn("2027-02-03", body)
        self.assertIn("3 February 2027", body)
        self.assertIn("Sol → Zebra", body)

    def test_published_scores_and_reasons_edit_appears_without_restart(self):
        self.edit(
            MODELS_REL,
            lambda t: t.replace("71.2%", "79.5%")
            .replace("Synthetic coding suite", "Updated coding suite")
            .replace(
                "Fixture-Alpha handles broad implementation fixtures.",
                "Updated fixture rationale bullet.",
            ),
        )
        _, body = self.request()
        recs_html = body[body.index('id="h-recs"') : body.index('id="h-allowance"')]
        self.assertIn("Updated coding suite", recs_html)
        self.assertIn("79.5%", recs_html)
        self.assertIn("Updated fixture rationale bullet.", recs_html)
        self.assertNotIn("71.2%", recs_html)
        self.assertNotIn("Synthetic coding suite", recs_html)


class UnsafeMarkdownTests(DashboardCase):
    def test_html_and_links_are_neutralised(self):
        def evil_models(text):
            text = text.replace("`gpt-6.1-sol`", "<script>alert('cell')</script>`<b>code</b>`")
            return text.replace("## Local evidence\n", "## Local evidence\n" + (
                "\n"
                "<img src=x onerror=alert(1)> and [bad](javascript:alert(1)) and "
                "[JS](JaVaScRiPt:alert(2)) and [data](data:text/html,<b>x</b>) and "
                "[rel](references/maintenance.md) and "
                '[quote](https://example.com/"onmouseover="x) and '
                "[user](https://user@evil.example/) and "
                "[good](https://example.com/a?b=1&c=2) and <https://auto.example>.\n"
            ), 1)

        self.edit(MODELS_REL, evil_models)
        self.edit(
            SKILL_REL,
            lambda t: t.replace("| Claude / Anthropic |", "| <svg onload=alert(3)> & Claude |"),
        )
        resp, body = self.request()
        self.assertEqual(resp.status, 200)
        low = body.lower()
        self.assertNotIn("<script", low)
        self.assertNotIn("<img", low)
        self.assertNotIn("<svg", low)
        self.assertNotIn("<b>", low)
        self.assertIn("&lt;script&gt;alert(&#x27;cell&#x27;)&lt;/script&gt;", body)
        self.assertIn("<code>&lt;b&gt;code&lt;/b&gt;</code>", body)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", body)
        self.assertIn("&lt;svg onload=alert(3)&gt; &amp; Claude", body)
        for bad in ('href="javascript', 'href="data:', 'href="references', "evil.example/\"", 'href="https://user@'):
            self.assertNotIn(bad.lower(), low, bad)
        self.assertIn('href="https://example.com/a?b=1&amp;c=2"', body)
        self.assertIn('rel="noopener noreferrer external"', body)
        # Unsafe links degrade to plain escaped text.
        self.assertIn("and bad and JS and data and rel and quote and user and", body)
        self.assertEqual(body.lower().count("href=\"https://example.com/"), 1)

    def test_safe_url_helper(self):
        ok = ["https://example.com", "http://localhost:8080/x?y=1#z"]
        bad = [
            "javascript:alert(1)", "data:text/html,x", "ftp://example.com", "//example.com",
            "https://u@example.com", "https://example.com/\"x", "https:///x", "vbscript:x",
            "https://exa mple.com", "https://example.com/\x01",
        ]
        for url in ok:
            self.assertEqual(dash.safe_url(url), url)
        for url in bad:
            self.assertIsNone(dash.safe_url(url), url)

    def test_inline_pipes_in_code_do_not_split_cells(self):
        row = dash.split_row("| a | `b | c` | d |")
        self.assertEqual(row, ["a", "`b | c`", "d"])

    def test_headings_and_score_table_content_escaped_and_unsafe_links_blocked(self):
        def inject_unsafe(text):
            text = text.replace(
                "### Synthetic coding suite",
                "### <script>alert('h')</script> [badhead](javascript:alert(1)) & Score",
            )
            text = text.replace(
                "| Fixture-Alpha | 71.2% |",
                "| <img src=x onerror=alert(2)> [data](data:text/html,<b>x</b>) [safe](https://example.org/scores?a=1&b=2) | 71.2% |",
            )
            return text.replace(
                "- Fixture-Alpha handles broad implementation fixtures.",
                "- <svg onload=alert(3)> [rel](references/secret.md)",
            )

        self.edit(MODELS_REL, inject_unsafe)
        resp, body = self.request()
        self.assertEqual(resp.status, 200)
        low = body.lower()
        self.assertNotIn("<script", low)
        self.assertNotIn("<img", low)
        self.assertNotIn("<svg", low)
        for bad in ('href="javascript', 'href="data:', 'href="references'):
            self.assertNotIn(bad, low)
        self.assertIn("&lt;script&gt;alert(&#x27;h&#x27;)&lt;/script&gt; badhead &amp; Score", body)
        self.assertIn("&lt;img src=x onerror=alert(2)&gt; data", body)
        self.assertIn("&lt;svg onload=alert(3)&gt; rel", body)
        self.assertIn('href="https://example.org/scores?a=1&amp;b=2"', body)
        self.assertIn('rel="noopener noreferrer external"', body)


class MissingInputTests(DashboardCase):
    def assert_generic_503(self):
        for path in ("/", "/healthz"):
            resp, body = self.request(path=path)
            self.assertEqual(resp.status, 503, path)
            self.assertEqual(resp.getheader("Cache-Control"), "no-store")
            for leak in (str(self.tmp), "Traceback", "SourceError", "server.py", "Errno", "SKILL.md", "models.md"):
                self.assertNotIn(leak, body, leak)
        _, health = self.request(path="/healthz")
        self.assertEqual(json.loads(health), {"status": "unavailable"})

    def test_missing_models_file(self):
        (self.tmp / MODELS_REL).unlink()
        self.assert_generic_503()

    def test_missing_skill_file(self):
        (self.tmp / SKILL_REL).unlink()
        self.assert_generic_503()

    def test_missing_assessed_date(self):
        self.edit(MODELS_REL, lambda t: t.replace("Assessed:", "Reviewed:"))
        self.assert_generic_503()

    def test_invalid_assessed_date(self):
        self.edit(MODELS_REL, lambda t: t.replace("2026-11-18", "2026-13-45", 1))
        self.assert_generic_503()

    def test_no_model_table(self):
        self.edit(MODELS_REL, lambda t: "\n".join(l for l in t.splitlines() if not l.startswith("|")))
        self.assert_generic_503()

    def test_no_rotation_table(self):
        self.edit(SKILL_REL, lambda t: "\n".join(l for l in t.splitlines() if not l.startswith("|")))
        self.assert_generic_503()

    def test_ragged_table(self):
        self.edit(SKILL_REL, lambda t: t.replace("| Sol → Hydrogen |", "| Sol → Hydrogen | extra |"))
        self.assert_generic_503()

    def test_invalid_utf8(self):
        (self.tmp / MODELS_REL).write_bytes(b"Assessed: 2026-11-18\n\xff\xfe")
        self.assert_generic_503()

    def test_oversized_source(self):
        (self.tmp / MODELS_REL).write_bytes(b"x" * (dash.MAX_SOURCE_BYTES + 10))
        self.assert_generic_503()

    def test_source_is_directory(self):
        (self.tmp / MODELS_REL).unlink()
        (self.tmp / MODELS_REL).mkdir()
        self.assert_generic_503()

    def test_recovers_when_source_restored(self):
        (self.tmp / MODELS_REL).unlink()
        self.assertEqual(self.request()[0].status, 503)
        (self.tmp / MODELS_REL).write_text(MODELS_FIXTURE, encoding="utf-8")
        self.assertEqual(self.request()[0].status, 200)

    def test_missing_optional_sections_still_render(self):
        def drop_sections(text):
            return text.split("## Local evidence")[0]

        self.edit(MODELS_REL, drop_sections)
        resp, body = self.request()
        self.assertEqual(resp.status, 200)
        self.assertIn("No local evidence is recorded", body)
        self.assertIn("No sources are recorded", body)

    def test_missing_published_scores_and_selection_reasons_omitted(self):
        def drop_between(text, start_marker, end_marker):
            before, rest = text.split(start_marker, 1)
            _, after = rest.split(end_marker, 1)
            return before + end_marker + after

        self.edit(MODELS_REL, lambda t: drop_between(t, "## Published scores", "## Selection reasons"))
        resp, body = self.request()
        self.assertEqual(resp.status, 200)
        self.assertNotIn("<h3>Published scores</h3>", body)
        self.assertIn("<h3>Selection reasons</h3>", body)

        (self.tmp / MODELS_REL).write_text(MODELS_FIXTURE, encoding="utf-8")
        self.edit(MODELS_REL, lambda t: drop_between(t, "## Selection reasons", "## Local evidence"))
        resp, body = self.request()
        self.assertEqual(resp.status, 200)
        self.assertIn("<h3>Published scores</h3>", body)
        self.assertNotIn("<h3>Selection reasons</h3>", body)

        (self.tmp / MODELS_REL).write_text(MODELS_FIXTURE, encoding="utf-8")
        self.edit(MODELS_REL, lambda t: drop_between(t, "## Published scores", "## Local evidence"))
        resp, body = self.request()
        self.assertEqual(resp.status, 200)
        self.assertNotIn("<h3>Published scores</h3>", body)
        self.assertNotIn("<h3>Selection reasons</h3>", body)
        self.assertIn("gpt-6.1-sol", body)

    def test_empty_published_scores_section_omitted(self):
        def empty_scores(text):
            before, rest = text.split("## Published scores", 1)
            _, after = rest.split("## Selection reasons", 1)
            return before + "## Published scores\n\n## Selection reasons" + after

        self.edit(MODELS_REL, empty_scores)
        resp, body = self.request()
        self.assertEqual(resp.status, 200)
        self.assertNotIn("<h3>Published scores</h3>", body)
        self.assertIn("<h3>Selection reasons</h3>", body)


class HttpBoundaryTests(DashboardCase):
    def test_binds_loopback_only(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")
        self.assertGreater(self.port, 0)

    def test_make_server_rejects_bad_ports(self):
        for port in (-1, 65536, "80", None, True):
            with self.assertRaises(ValueError):
                dash.make_server(port, repo_root=self.tmp)

    def test_only_expected_paths_are_served(self):
        for path in (
            "/skills/model-use/SKILL.md",
            "/skills/model-use/references/models.md",
            "/skills/",
            "/skills",
            "/dashboard/server.py",
            "/dashboard/index.html",
            "/dashboard/",
            "/.git/config",
            "/.git/",
            "/.model-use/state.json",
            "/README.md",
            "/../README.md",
            "/%2e%2e/README.md",
            "/%2fetc/passwd",
            "//etc/passwd",
            "/healthz/",
            "/index.html/",
            "/favicon.ico",
            "/static/",
        ):
            resp, body = self.request(path=path)
            self.assertEqual(resp.status, 404, path)
            self.assertNotIn("Index of", body)
            self.assertNotIn("model-use", body.lower())

    def test_absolute_form_target_rejected(self):
        resp, _ = self.request(path="http://127.0.0.1/")
        self.assertEqual(resp.status, 404)

    def test_write_methods_rejected_without_cors(self):
        for method in ("POST", "PUT", "DELETE", "PATCH", "OPTIONS"):
            resp, _ = self.request(method, "/")
            self.assertEqual(resp.status, 405, method)
            self.assertEqual(resp.getheader("Allow"), "GET, HEAD")
            self.assertIsNone(resp.getheader("Access-Control-Allow-Origin"))
        resp, _ = self.request("OPTIONS", "/healthz", headers={"Origin": "https://evil.example"})
        self.assertIsNone(resp.getheader("Access-Control-Allow-Origin"))

    def test_unknown_method_is_generic(self):
        resp, body = self.request("BREW", "/")
        self.assertIn(resp.status, (405, 501))
        self.assertEqual(resp.getheader("Cache-Control"), "no-store")
        self.assertNotIn("Traceback", body)

    def test_host_validation(self):
        port = self.port
        for host in (f"127.0.0.1:{port}", f"localhost:{port}", f"LOCALHOST:{port}"):
            self.assertEqual(self.request(host=host)[0].status, 200, host)
        for host in (
            "evil.example",
            f"evil.example:{port}",
            "127.0.0.1",
            "localhost",
            f"127.0.0.1:{port + 1}",
            f"127.0.0.1:{port}.evil.example",
            f"[::1]:{port}",
            f"0.0.0.0:{port}",
            f"user@127.0.0.1:{port}",
            "",
        ):
            for path in ("/", "/healthz", "/nope"):
                resp, body = self.request(path=path, host=host)
                self.assertEqual(resp.status, 403, f"{host!r} {path}")
                self.assertNotIn("Current recommendations", body)

    def test_missing_and_duplicate_host_header_rejected(self):
        for raw in (
            b"GET / HTTP/1.0\r\n\r\n",
            f"GET / HTTP/1.0\r\nHost: 127.0.0.1:{self.port}\r\nHost: evil.example\r\n\r\n".encode(),
        ):
            with socket.create_connection(("127.0.0.1", self.port), timeout=5) as sock:
                sock.sendall(raw)
                data = b""
                while chunk := sock.recv(4096):
                    data += chunk
            self.assertTrue(data.startswith(b"HTTP/1.0 403"), data[:40])

    def test_security_headers_on_every_response_kind(self):
        responses = [
            self.request(path="/")[0],
            self.request(path="/healthz")[0],
            self.request(path="/missing")[0],
            self.request(host="evil.example")[0],
            self.request("POST")[0],
        ]
        for resp in responses:
            self.assertEqual(resp.getheader("Cache-Control"), "no-store")
            self.assertEqual(resp.getheader("X-Content-Type-Options"), "nosniff")
            self.assertEqual(resp.getheader("Referrer-Policy"), "no-referrer")
            self.assertEqual(resp.getheader("X-Frame-Options"), "DENY")
            csp = resp.getheader("Content-Security-Policy")
            self.assertIn("default-src 'none'", csp)
            self.assertIn("frame-ancestors 'none'", csp)
            self.assertNotIn("script-src", csp)
            self.assertIsNone(resp.getheader("Access-Control-Allow-Origin"))
            self.assertNotIn("Python", resp.getheader("Server", ""))

    def test_malformed_request_gets_generic_error(self):
        with socket.create_connection(("127.0.0.1", self.port), timeout=5) as sock:
            sock.sendall(b"NOT A REQUEST\r\n\r\n")
            data = b""
            while chunk := sock.recv(4096):
                data += chunk
        self.assertNotIn(b"Traceback", data)
        self.assertIn(b"no-store", data)


class CommandLineTests(unittest.TestCase):
    def test_invalid_port_rejected(self):
        for value in ("70000", "-1", "abc"):
            proc = subprocess.run(
                [sys.executable, "-I", str(SERVER_PY), "--port", value],
                capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(proc.returncode, 2, value)

    def test_cli_serves_and_stops(self):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        proc = subprocess.Popen(
            [sys.executable, "-I", str(SERVER_PY), "--port", str(port)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            status = None
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline and status is None:
                try:
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
                    conn.request("GET", "/", headers={"Host": f"127.0.0.1:{port}"})
                    resp = conn.getresponse()
                    body = resp.read().decode()
                    status = resp.status
                    conn.close()
                except OSError:
                    time.sleep(0.1)
            self.assertEqual(status, 200)
            self.assertIn("Current recommendations", body)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        self.assertIsNotNone(proc.returncode)


if __name__ == "__main__":
    unittest.main()
