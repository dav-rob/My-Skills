"""Credential bridge checks use fake secrets and never touch a real Keychain."""
import contextlib
import ctypes
import http.client
import importlib.util
import io
import json
from pathlib import Path
import threading
import unittest

spec = importlib.util.spec_from_file_location("mac_login_credentials", Path(__file__).resolve().parents[1] / "skills/mac-login/scripts/credentials.py")
credentials = importlib.util.module_from_spec(spec)
spec.loader.exec_module(credentials)


class FakeKeychain:
    def __init__(self):
        self.value = {"username": "fixture@example.invalid", "password": "fixture-only-secret"}
        self.reads = 0
        self.saves = 0
        self.fail = False

    def save(self, value):
        self.value = credentials.validate_credentials(value)
        self.saves += 1

    def read(self):
        self.reads += 1
        if self.fail:
            raise credentials.CredentialError("Login unavailable without an interactive unlock (status -25308).")
        return self.value


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.keychain = FakeKeychain()
        self.server = credentials.make_server(self.keychain, 'https://example.invalid', 'com.example.mac-login', 'example.invalid')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def request(self, path, body=None, headers=None, method="POST"):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=2)
        defaults = {"Origin": self.server.origin, "Content-Type": "application/json", "X-Setup-Token": self.server.token}
        defaults.update(headers or {})
        connection.request(method, path, body=json.dumps(body or {}) if method == "POST" else None, headers=defaults)
        response = connection.getresponse()
        result = (response.status, dict(response.headers), response.read())
        connection.close()
        return result

    def test_setup_and_static_files_never_read_or_echo_login(self):
        for path in ("/", "/style.css", "/app.js"):
            status, headers, body = self.request(path, method="GET")
            self.assertEqual(status, 200)
            self.assertEqual(headers["Cache-Control"], "no-store")
            self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
            self.assertNotIn(self.keychain.value["password"].encode(), body)
        self.assertEqual(self.keychain.reads, 0)

    def test_rebinding_foreign_origin_and_wrong_token_block_reads_and_writes(self):
        for header in ({"Host": "attacker.invalid"}, {"Origin": "https://attacker.invalid"},
                       {"Origin": "null"}, {"Origin": ""}, {"X-Setup-Token": "wrong"}):
            for path in ("/save", "/copy", "/check"):
                self.assertEqual(self.request(path, self.keychain.value, header)[0], 403)
        self.assertEqual(self.keychain.reads, 0)
        self.assertEqual(self.keychain.saves, 0)
        self.assertEqual(self.request("/", headers={"Host": "attacker.invalid"}, method="GET")[0], 403)

    def test_save_and_check_do_not_echo_credentials_or_log_requests(self):
        output = io.StringIO()
        with contextlib.redirect_stderr(output), contextlib.redirect_stdout(output):
            saved = self.request("/save", self.keychain.value)
            checked = self.request("/check")
        self.assertEqual(saved[0], 200)
        self.assertEqual(checked[0], 200)
        self.assertEqual(output.getvalue(), "")
        for value in self.keychain.value.values():
            self.assertNotIn(value.encode(), saved[2])
            self.assertNotIn(value.encode(), checked[2])

    def test_copy_requires_valid_field_and_only_returns_that_field(self):
        for field in ("username", "password"):
            status, headers, body = self.request("/copy", {"field": field})
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(body), {"value": self.keychain.value[field]})
            self.assertEqual(headers["Cache-Control"], "no-store")
        reads = self.keychain.reads
        self.assertEqual(self.request("/copy", {"field": "anything"})[0], 400)
        self.assertEqual(self.keychain.reads, reads)

    def test_unattended_unlock_failure_is_visible_without_secret(self):
        self.keychain.fail = True
        for path in ("/copy", "/check"):
            status, _, body = self.request(path, {"field": "password"})
            self.assertEqual(status, 400)
            self.assertIn(b"interactive unlock", body)
            self.assertNotIn(self.keychain.value["password"].encode(), body)

    def test_bad_input_is_rejected_without_echo(self):
        for value in ({"username": "", "password": "fixture-only-secret"},
                      {"username": "fixture", "password": ""},
                      {"username": "fixture", "password": 123},
                      {"username": "fixture", "password": "secret", "extra": "x"}, []):
            status, _, body = self.request("/save", value)
            self.assertEqual(status, 400)
            self.assertNotIn(b"fixture-only-secret", body)
        self.assertEqual(self.keychain.saves, 0)
        self.assertEqual(self.request("/save", headers={"Content-Length": "9000"})[0], 400)


class NativeReadTests(unittest.TestCase):
    def test_interaction_policy_restored_on_failed_read(self):
        class FakeLibrary:
            def __init__(self):
                self.settings = []

            def SecKeychainGetUserInteractionAllowed(self, out):
                ctypes.cast(out, ctypes.POINTER(ctypes.c_ubyte))[0] = 1
                return 0

            def SecKeychainSetUserInteractionAllowed(self, allowed):
                self.settings.append(allowed)
                return 0

            def SecKeychainFindGenericPassword(self, *args):
                return -25308

        keychain = credentials.MacKeychain.__new__(credentials.MacKeychain)
        keychain.service, keychain.account = b'com.example.mac-login', b'example.invalid'
        keychain.lib = FakeLibrary()
        with self.assertRaises(credentials.CredentialError):
            keychain.read()
        self.assertEqual(keychain.lib.settings, [False, 1])


class ScopeTests(unittest.TestCase):
    def test_explicit_scope_accepts_existing_rightmove_item(self):
        self.assertEqual(credentials.validate_scope('com.davrob.auction-properties.rightmove-sync', 'rightmove.co.uk', 'https://www.rightmove.co.uk/'),
                         (b'com.davrob.auction-properties.rightmove-sync', b'rightmove.co.uk', 'https://www.rightmove.co.uk'))

    def test_scope_rejects_secret_urls_and_unsafe_item_keys(self):
        for site in ('http://example.invalid', 'https://user:secret@example.invalid',
                     'https://example.invalid/?secret=x', 'https://example.invalid/#secret', 'https://example.invalid/login'):
            with self.assertRaises(credentials.CredentialError):
                credentials.validate_scope('com.example.mac-login', 'example.invalid', site)
        for service, account in (('', 'example.invalid'), ('com.example.mac-login', ''),
                                 ('com.example.mac-login', 'user@example.invalid'), ('bad\nkey', 'example.invalid')):
            with self.assertRaises(credentials.CredentialError):
                credentials.validate_scope(service, account, 'https://example.invalid')


if __name__ == "__main__":
    unittest.main()
