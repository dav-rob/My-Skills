#!/usr/bin/env python3
"""Read-only localhost dashboard for the model-use skill.

Serves a concise summary rendered on every request from the canonical markdown:

    skills/model-use/SKILL.md
    skills/model-use/references/models.md

Standard library only. Binds 127.0.0.1 exclusively. Serves only "/",
"/index.html" and "/healthz"; there are no write or control endpoints.

    python3 dashboard/server.py [--port N]
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import re
import signal
import socketserver
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DEFAULT_PORT = 48173
LOOPBACK = "127.0.0.1"
MAX_SOURCE_BYTES = 256 * 1024
MAX_TABLE_COLUMNS = 12

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent
TEMPLATE_PATH = HERE / "index.html"
SKILL_REL = ("skills", "model-use", "SKILL.md")
MODELS_REL = ("skills", "model-use", "references", "models.md")

# Short stable rules, each shown as the sentence(s) found in SKILL.md that
# contain the marker. If the marker disappears from the source the rule is
# simply omitted, so the page never states something the source no longer says.
BEHAVIOUR_RULES = (
    ("The manager stays accountable", "Keep the model the user is talking to", 2),
    ("The manager is identified by model family", "Identify the manager by", 1),
    ("One slot, two routes", "Sonnet is one slot", 1),
    ("Every worker gets real work", "Hydrogen gets ordinary work", 1),
    ("Work is verified", "Require the CLI's successful terminal result", 1),
    ("Fail over once", "Make at most one pass", 1),
    ("The manager is the last resort", "If all eligible workers are unavailable", 1),
    ("No spending", "Do not buy credits", 1),
    ("Allowance is not comparable", "token counts are not interchangeable", 1),
)

SECURITY_HEADERS = (
    ("Cache-Control", "no-store"),
    ("Pragma", "no-cache"),
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "no-referrer"),
    ("Cross-Origin-Resource-Policy", "same-origin"),
    ("Cross-Origin-Opener-Policy", "same-origin"),
    ("Permissions-Policy", "camera=(), microphone=(), geolocation=(), interest-cohort=()"),
    (
        "Content-Security-Policy",
        "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; "
        "form-action 'none'; frame-ancestors 'none'",
    ),
)


class SourceError(Exception):
    """A required source is missing or not in the expected shape.

    Messages are for tests/diagnostics only and are never sent to clients.
    """


# --------------------------------------------------------------------------
# Reading and parsing the markdown sources
# --------------------------------------------------------------------------

def read_text(root: Path, rel: tuple[str, ...]) -> str:
    path = Path(root).joinpath(*rel)
    try:
        with open(path, "rb") as handle:
            data = handle.read(MAX_SOURCE_BYTES + 1)
    except OSError as exc:
        raise SourceError("unreadable source") from exc
    if len(data) > MAX_SOURCE_BYTES:
        raise SourceError("source too large")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SourceError("source is not UTF-8") from exc


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[index + 1 :])
    return text


def split_sections(text: str) -> list[dict]:
    """Split on markdown headings, ignoring fenced code blocks."""
    sections = [{"level": 0, "title": "", "lines": []}]
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            sections[-1]["lines"].append(line)
            continue
        match = None if in_fence else re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if match:
            sections.append({"level": len(match.group(1)), "title": match.group(2), "lines": []})
        else:
            sections[-1]["lines"].append(line)
    return sections


def split_row(line: str) -> list[str]:
    """Split a markdown table row on pipes that are not inside backticks."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    cells, current, in_code, index = [], [], False, 0
    while index < len(line):
        char = line[index]
        if char == "\\" and line[index + 1 : index + 2] == "|":
            current.append("|")
            index += 2
            continue
        if char == "`":
            in_code = not in_code
        if char == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$")


def parse_table(lines: list[str]) -> dict:
    if len(lines) < 3 or not _SEPARATOR.match(lines[1]):
        raise SourceError("malformed table")
    header = split_row(lines[0])
    if not 1 <= len(header) <= MAX_TABLE_COLUMNS:
        raise SourceError("malformed table")
    rows = [split_row(line) for line in lines[2:]]
    if any(len(row) != len(header) for row in rows):
        raise SourceError("malformed table")
    return {"type": "table", "header": header, "rows": rows}


def parse_blocks(lines: list[str]) -> list[dict]:
    """Return headings, paragraphs, bullet lists and tables; fenced code is dropped."""
    blocks: list[dict] = []
    para: list[str] = []
    table: list[str] = []
    items: list[str] = []
    in_fence = False

    def flush() -> None:
        if para:
            blocks.append({"type": "p", "text": " ".join(para)})
        if table:
            blocks.append(parse_table(table))
        if items:
            blocks.append({"type": "ul", "items": list(items)})
        para.clear()
        table.clear()
        items.clear()

    for raw in lines:
        line = raw.rstrip()
        if line.lstrip().startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if not stripped:
            flush()
        elif match := re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", stripped):
            flush()
            blocks.append({"type": "heading", "level": len(match.group(1)), "text": match.group(2)})
        elif stripped.startswith("|"):
            if para or items:
                flush()
            table.append(stripped)
        elif re.match(r"^[-*]\s+", stripped):
            if para or table:
                flush()
            items.append(re.sub(r"^[-*]\s+", "", stripped))
        elif items and raw[:1].isspace():
            items[-1] += " " + stripped
        else:
            if table or items:
                flush()
            para.append(stripped)
    flush()
    return blocks


def first_table(blocks: list[dict]) -> dict | None:
    return next((block for block in blocks if block["type"] == "table"), None)


def find_section(sections: list[dict], needle: str) -> dict | None:
    needle = needle.lower()
    return next((s for s in sections if s["level"] and needle in s["title"].lower()), None)


def collect_section(sections: list[dict], needle: str) -> tuple[str, list[dict]] | None:
    """Return (title, blocks) for a matching section, including nested subheadings."""
    needle_low = needle.lower()
    start = next(
        (
            index
            for index, section in enumerate(sections)
            if section["level"] == 2 and needle_low in section["title"].lower()
        ),
        None,
    )
    if start is None:
        start = next(
            (
                index
                for index, section in enumerate(sections)
                if section["level"] and needle_low in section["title"].lower()
            ),
            None,
        )
    if start is None:
        return None
    base_level = sections[start]["level"]
    blocks = parse_blocks(sections[start]["lines"])
    for sub in sections[start + 1 :]:
        if sub["level"] <= base_level:
            break
        blocks.append({"type": "heading", "level": sub["level"], "text": sub["title"]})
        blocks.extend(parse_blocks(sub["lines"]))
    return sections[start]["title"], blocks


def sentences(blocks: list[dict]) -> list[str]:
    found: list[str] = []
    for block in blocks:
        if block["type"] == "p":
            found.extend(s for s in re.split(r"(?<=[.!?])\s+", block["text"]) if s)
    return found


def parse_sources(skill_text: str, models_text: str) -> dict:
    skill_body = strip_frontmatter(skill_text)
    skill_sections = split_sections(skill_body)

    rotation_section = find_section(skill_sections, "round robin")
    rotation = first_table(parse_blocks(rotation_section["lines"])) if rotation_section else None
    if rotation is None or not rotation["rows"]:
        raise SourceError("rotation table missing")

    all_sentences: list[str] = []
    for section in skill_sections:
        all_sentences.extend(sentences(parse_blocks(section["lines"])))
    rules = []
    for title, marker, count in BEHAVIOUR_RULES:
        for index, sentence in enumerate(all_sentences):
            if marker in sentence:
                rules.append((title, " ".join(all_sentences[index : index + count])))
                break

    match = re.search(r"^Assessed:\s*(\d{4}-\d{2}-\d{2})\b", models_text, re.MULTILINE)
    if not match:
        raise SourceError("assessed date missing")
    try:
        assessed = datetime.date.fromisoformat(match.group(1))
    except ValueError as exc:
        raise SourceError("assessed date invalid") from exc

    models_sections = split_sections(models_text)
    models_section = next(
        (s for s in models_sections if s["level"] and first_table(parse_blocks(s["lines"]))), None
    )
    if models_section is None:
        raise SourceError("model table missing")
    models_blocks = parse_blocks(models_section["lines"])
    models = first_table(models_blocks)
    if not models["rows"]:
        raise SourceError("model table empty")
    table_index = models_blocks.index(models)

    def blocks_of(needle: str) -> list[dict]:
        found = collect_section(models_sections, needle)
        return found[1] if found else []

    return {
        "rotation": rotation,
        "rules": rules,
        "assessed": assessed,
        "models": models,
        "models_before": models_blocks[:table_index],
        "models_after": models_blocks[table_index + 1 :],
        "published_scores": collect_section(models_sections, "published scores"),
        "selection_reasons": collect_section(models_sections, "selection reasons"),
        "evidence": blocks_of("local evidence"),
        "sources": blocks_of("assessment sources"),
    }


# --------------------------------------------------------------------------
# Escaping and HTML helpers
# --------------------------------------------------------------------------

_INLINE = re.compile(r"`([^`]+)`|\[([^\]]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)")
_SAFE_URL = re.compile(
    r"^https?://[A-Za-z0-9.-]+(:\d{1,5})?([/?#][^\s<>\"'`\\\x00-\x1f\x7f]*)?$", re.IGNORECASE
)


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def safe_url(url: str) -> str | None:
    """Return the URL only if it is a plain http/https link."""
    return url if _SAFE_URL.match(url) else None


def inline(text: str) -> str:
    """Escape text, rendering only `code` and [text](http(s) url)."""
    out, position = [], 0
    for match in _INLINE.finditer(text):
        out.append(esc(text[position : match.start()]))
        if match.group(1) is not None:
            out.append("<code>" + esc(match.group(1)) + "</code>")
        else:
            label, url = match.group(2), safe_url(match.group(3))
            if url:
                out.append(
                    f'<a href="{esc(url)}" rel="noopener noreferrer external">{esc(label)}</a>'
                )
            else:
                out.append(esc(label))
        position = match.end()
    out.append(esc(text[position:]))
    return "".join(out)


def render_table(table: dict, label: str) -> str:
    head = "".join(f'<th scope="col">{inline(cell)}</th>' for cell in table["header"])
    body = []
    for row in table["rows"]:
        first, rest = row[0], row[1:]
        cells = f'<th scope="row">{inline(first)}</th>' + "".join(
            f"<td>{inline(cell)}</td>" for cell in rest
        )
        body.append(f"<tr>{cells}</tr>")
    return (
        f'<div class="table-wrap" role="region" aria-label="{esc(label)}" tabindex="0">'
        f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def render_blocks(blocks: list[dict], label: str = "Table", heading_offset: int = 0) -> str:
    out = []
    current_label = label
    for block in blocks:
        if block["type"] == "heading":
            tag_level = min(6, max(3, block["level"] + heading_offset))
            current_label = block["text"]
            out.append(f"<h{tag_level}>{inline(block['text'])}</h{tag_level}>")
        elif block["type"] == "p":
            out.append(f"<p>{inline(block['text'])}</p>")
        elif block["type"] == "ul":
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in block["items"]) + "</ul>")
        elif block["type"] == "table":
            out.append(render_table(block, current_label))
    return "\n".join(out)


def render_subsection(section: tuple[str, list[dict]] | None) -> str:
    if not section:
        return ""
    title, blocks = section
    body = render_blocks(blocks, label=title, heading_offset=1)
    if not body:
        return ""
    return f'<div class="rec-sub">\n<h3>{inline(title)}</h3>\n{body}\n</div>'


def render_rules(rules: list[tuple[str, str]]) -> str:
    if not rules:
        return "<p>No behaviour summary is available.</p>"
    return '<ul class="rules">' + "".join(
        f"<li><strong>{esc(title)}</strong><span>{inline(text)}</span></li>" for title, text in rules
    ) + "</ul>"


def render_assessor(models: dict) -> str:
    for row in models["rows"]:
        if "assessor" in row[0].lower():
            items = "".join(
                f"<div><dt>{inline(label)}</dt><dd>{inline(value)}</dd></div>"
                for label, value in zip(models["header"], row)
            )
            return f'<dl class="facts">{items}</dl>'
    return ""


def age_note(assessed: datetime.date, today: datetime.date) -> str:
    days = (today - assessed).days
    if days < 0:
        return ""
    when = "today" if days == 0 else "1 day ago" if days == 1 else f"{days} days ago"
    # A successful no-change weekly review intentionally leaves this date alone.
    # Assessment age is not evidence that the scheduled review failed.
    return f"Assessed {when}."


def render_page(repo_root: Path, today: datetime.date | None = None) -> str:
    """Render the dashboard from the current files on disk."""
    today = today or datetime.date.today()
    try:
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SourceError("template unavailable") from exc
    data = parse_sources(read_text(repo_root, SKILL_REL), read_text(repo_root, MODELS_REL))
    assessed = data["assessed"]
    evidence = render_blocks(data["evidence"]) or "<p>No local evidence is recorded.</p>"
    sources = render_blocks(data["sources"]) or "<p>No sources are recorded.</p>"
    values = {
        "ASSESSED_ISO": assessed.isoformat(),
        "ASSESSED_HUMAN": f"{assessed.day} {assessed.strftime('%B %Y')}",
        "AGE_NOTE": age_note(assessed, today),
        "ROTATION_TABLE": render_table(data["rotation"], "Worker order by project manager"),
        "RULES": render_rules(data["rules"]),
        "MODELS_INTRO": render_blocks(data["models_before"]),
        "MODELS_TABLE": render_table(data["models"], "Recommended models, routes and efforts"),
        "ESCALATION": render_blocks(data["models_after"]),
        "PUBLISHED_SCORES": render_subsection(data["published_scores"]),
        "SELECTION_REASONS": render_subsection(data["selection_reasons"]),
        "ASSESSOR": render_assessor(data["models"]),
        "EVIDENCE": evidence,
        "SOURCES": sources,
    }
    # Single pass: substituted markdown is never re-scanned for tokens.
    return re.sub(r"%%([A-Z_]+)%%", lambda m: values.get(m.group(1), ""), template)


UNAVAILABLE_PAGE = (
    "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
    "<title>Model use: unavailable</title>"
    "<style>body{font:16px/1.5 system-ui,sans-serif;max-width:40rem;margin:4rem auto;"
    "padding:0 1rem;color:#14213d}</style></head><body><h1>Summary unavailable</h1>"
    "<p>The model-use notes could not be read or are not in the expected format. "
    "Fix the notes and reload this page.</p></body></html>"
)


# --------------------------------------------------------------------------
# HTTP server
# --------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    sys_version = ""
    server_version = "ModelUseDashboard"
    protocol_version = "HTTP/1.0"
    timeout = 10

    def version_string(self) -> str:
        return self.server_version

    def log_message(self, format: str, *args) -> None:  # noqa: A002 - stdlib signature
        pass

    # -- responses ---------------------------------------------------------

    def _respond(self, status: int, body: bytes, content_type: str, extra=()) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in SECURITY_HEADERS:
            self.send_header(name, value)
        for name, value in extra:
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _text(self, status: int, extra=()) -> None:
        body = (HTTPStatus(status).phrase + "\n").encode("ascii")
        self._respond(status, body, "text/plain; charset=utf-8", extra)

    def send_error(self, code, message=None, explain=None) -> None:  # stdlib signature
        try:
            self._text(int(code))
        except (ValueError, OSError):
            self.close_connection = True

    # -- request checks ----------------------------------------------------

    def _host_allowed(self) -> bool:
        hosts = self.headers.get_all("Host") or []
        if len(hosts) != 1:
            return False
        port = self.server.server_address[1]
        return hosts[0].strip().lower() in (f"127.0.0.1:{port}", f"localhost:{port}")

    def _serve(self) -> None:
        if not self._host_allowed():
            return self._text(HTTPStatus.FORBIDDEN)
        target = self.path
        path = target.split("?", 1)[0].split("#", 1)[0]
        if not target.startswith("/"):
            return self._text(HTTPStatus.NOT_FOUND)
        if path in ("/", "/index.html"):
            try:
                page = render_page(self.server.repo_root)
            except Exception:  # never leak details of a failure to the client
                return self._respond(
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    UNAVAILABLE_PAGE.encode("utf-8"),
                    "text/html; charset=utf-8",
                )
            return self._respond(HTTPStatus.OK, page.encode("utf-8"), "text/html; charset=utf-8")
        if path == "/healthz":
            try:
                render_page(self.server.repo_root)
                status, payload = HTTPStatus.OK, {"status": "ok"}
            except Exception:
                status, payload = HTTPStatus.SERVICE_UNAVAILABLE, {"status": "unavailable"}
            return self._respond(
                status, (json.dumps(payload) + "\n").encode("ascii"), "application/json"
            )
        return self._text(HTTPStatus.NOT_FOUND)

    def do_GET(self) -> None:  # noqa: N802
        self._serve()

    def do_HEAD(self) -> None:  # noqa: N802
        self._serve()

    def _method_not_allowed(self) -> None:
        if not self._host_allowed():
            return self._text(HTTPStatus.FORBIDDEN)
        self._text(HTTPStatus.METHOD_NOT_ALLOWED, extra=(("Allow", "GET, HEAD"),))

    do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = _method_not_allowed  # noqa: N815


class DashboardServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    repo_root: Path = DEFAULT_ROOT

    def server_bind(self) -> None:
        # Skip HTTPServer's reverse-DNS lookup of the bound address.
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name, self.server_port = host, port


def make_server(port: int = DEFAULT_PORT, repo_root=None) -> DashboardServer:
    """Create (but do not start) a server bound only to 127.0.0.1.

    Use port=0 for an ephemeral port; read it from server.server_address[1].
    """
    if not isinstance(port, int) or isinstance(port, bool) or not 0 <= port <= 65535:
        raise ValueError("port must be an integer between 0 and 65535")
    server = DashboardServer((LOOPBACK, port), Handler)
    server.repo_root = Path(repo_root) if repo_root is not None else DEFAULT_ROOT
    return server


def port_arg(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be a number") from exc
    if not 0 <= number <= 65535:
        raise argparse.ArgumentTypeError("port must be between 0 and 65535")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only local model-use dashboard.")
    parser.add_argument("--port", type=port_arg, default=DEFAULT_PORT, help="port on 127.0.0.1")
    args = parser.parse_args(argv)
    try:
        server = make_server(args.port)
    except OSError:
        print("Could not start the dashboard; is the port already in use?", file=sys.stderr)
        return 1

    def stop(signum, frame):  # noqa: ARG001
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    print(f"Model-use dashboard: http://{LOOPBACK}:{server.server_address[1]}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
