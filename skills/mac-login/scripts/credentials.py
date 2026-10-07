#!/usr/bin/env python3
"""Scoped Mac Keychain setup/clipboard bridge; never print credential values."""

import argparse
import ctypes
import html
import json
import secrets
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

MAX_BODY = 8192


class CredentialError(Exception):
    """Contains a fixed message/status only, never supplied credentials."""


def validate_scope(service, account, site):
    for value in (service, account):
        if (not isinstance(value, str) or not value or len(value) > 200
                or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-' for c in value)):
            raise CredentialError("Use non-secret service/account identifiers containing letters, digits, dots, underscores or hyphens.")
    parsed = urlsplit(site)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/')):
        raise CredentialError("Use an HTTPS website origin without credentials, query or fragment.")
    return service.encode(), account.encode(), site.rstrip('/')


def validate_credentials(value):
    if (not isinstance(value, dict) or set(value) != {"username", "password"}
            or not all(isinstance(value[k], str) for k in value)):
        raise CredentialError("Enter a username and password.")
    username, password = value["username"].strip(), value["password"]
    if not username or not password or len(username) > 512 or len(password) > 2048:
        raise CredentialError("Enter a valid username and password.")
    return {"username": username, "password": password}


class MacKeychain:
    """Own generic item only. Reads fail instead of displaying unlock dialogs."""

    def __init__(self, service, account):
        if sys.platform != "darwin":
            raise CredentialError("This helper requires macOS.")
        self.service, self.account = service, account
        self.lib = ctypes.CDLL("/System/Library/Frameworks/Security.framework/Security")
        u32, ptr, char = ctypes.c_uint32, ctypes.c_void_p, ctypes.c_char_p
        self.lib.SecKeychainAddGenericPassword.argtypes = [ptr, u32, char, u32, char, u32, ptr, ptr]
        self.lib.SecKeychainAddGenericPassword.restype = ctypes.c_int32
        self.lib.SecKeychainFindGenericPassword.argtypes = [ptr, u32, char, u32, char, ctypes.POINTER(u32), ctypes.POINTER(ptr), ptr]
        self.lib.SecKeychainFindGenericPassword.restype = ctypes.c_int32
        self.lib.SecKeychainItemFreeContent.argtypes = [ptr, ptr]
        self.lib.SecKeychainItemFreeContent.restype = ctypes.c_int32
        self.lib.SecKeychainSetUserInteractionAllowed.argtypes = [ctypes.c_ubyte]
        self.lib.SecKeychainSetUserInteractionAllowed.restype = ctypes.c_int32
        self.lib.SecKeychainGetUserInteractionAllowed.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        self.lib.SecKeychainGetUserInteractionAllowed.restype = ctypes.c_int32

    def save(self, value):
        data = json.dumps(validate_credentials(value), ensure_ascii=False).encode("utf-8")
        buffer = ctypes.create_string_buffer(data)
        status = self.lib.SecKeychainAddGenericPassword(None, len(self.service), self.service,
            len(self.account), self.account, len(data), buffer, None)
        if status == -25299:
            raise CredentialError("A login already exists. Manage this item in Keychain Access before replacing it.")
        if status:
            raise CredentialError(f"Keychain save failed (status {status}).")

    def read(self):
        old = ctypes.c_ubyte()
        if self.lib.SecKeychainGetUserInteractionAllowed(ctypes.byref(old)):
            raise CredentialError("Cannot verify Keychain interaction policy.")
        if self.lib.SecKeychainSetUserInteractionAllowed(False):
            raise CredentialError("Cannot disable interactive Keychain prompts.")
        length, data = ctypes.c_uint32(), ctypes.c_void_p()
        try:
            status = self.lib.SecKeychainFindGenericPassword(None, len(self.service), self.service,
                len(self.account), self.account, ctypes.byref(length), ctypes.byref(data), None)
            if status == -25300:
                raise CredentialError("No login has been saved for this service/account.")
            if status:
                raise CredentialError(f"Login unavailable without an interactive unlock (status {status}).")
            try:
                return validate_credentials(json.loads(ctypes.string_at(data, length.value)))
            except (ValueError, UnicodeError):
                raise CredentialError("Stored login is invalid.") from None
            finally:
                self.lib.SecKeychainItemFreeContent(None, data)
        finally:
            self.lib.SecKeychainSetUserInteractionAllowed(old.value)


PAGE = b'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mac website login setup</title><link rel="stylesheet" href="/style.css">
<main><h1>Mac website login setup</h1>
<p>Website: <strong>__SITE__</strong></p>
<p>Keychain service: __SERVICE__<br>Account key: __ACCOUNT__</p>
<p>Enter the website login to store a dedicated item in this Mac's Keychain.
Saving authorizes later retrieval by this helper for the agreed website task.</p>
<p>This setup does not sign in or change your website account.</p>
<form id="setup" autocomplete="off">
<label>Website username or email<input id="username" type="text" required maxlength="512" autocomplete="off"></label>
<label>Website password<input id="password" type="password" required maxlength="2048" autocomplete="new-password"></label>
<button>Save login to Mac Keychain</button></form>
<h2>Login test</h2><p>These buttons copy one field for pasting into the agreed website.
No credential values are displayed. An interactive unlock causes a failure.</p>
<button id="check">Check unattended access</button>
<button id="copy-user">Copy username</button><button id="copy-password">Copy password</button>
<button id="clear">Clear clipboard</button>
<p id="status" role="status"></p><script src="/app.js"></script></main></html>'''

CSS = b'''body{font:18px system-ui;background:#f5f7fa;color:#172333;margin:0}
main{max-width:650px;margin:3rem auto;padding:2rem;background:white;border-radius:12px}
label{display:block;margin:1rem 0}input{display:block;width:95%;font:inherit;padding:.7rem}
button{font:inherit;padding:.65rem;margin:.3rem;cursor:pointer}h2{margin-top:2rem}
#status{white-space:pre-wrap;min-height:2rem}'''

JS = b'''"use strict";
const token=location.hash.slice(1);history.replaceState(null,"",location.pathname);
const status=document.getElementById("status");
async function call(path,body={}){
 const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json","X-Setup-Token":token},body:JSON.stringify(body),cache:"no-store"});
 const data=await r.json();if(!r.ok)throw Error(data.message);return data;
}
document.getElementById("setup").onsubmit=async e=>{
 e.preventDefault();const p=document.getElementById("password"),u=document.getElementById("username");
 try{const result=await call("/save",{username:u.value,password:p.value});p.value="";u.value="";status.textContent=result.message;}
 catch(e){status.textContent=e.message;}
};
document.getElementById("check").onclick=async()=>{try{status.textContent=(await call("/check")).message;}catch(e){status.textContent=e.message;}};
for(const [id,field] of [["copy-user","username"],["copy-password","password"]]){
 document.getElementById(id).onclick=async()=>{try{const data=await call("/copy",{field});await navigator.clipboard.writeText(data.value);data.value="";status.textContent="Copied "+field+" for website login. Clear the clipboard after signing in.";}catch(e){status.textContent=e.message;}};
}
document.getElementById("clear").onclick=async()=>{try{await navigator.clipboard.writeText("");status.textContent="Clipboard cleared.";}catch(e){status.textContent="Clipboard clearing failed.";}};
'''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass  # Never log request paths, bodies or credentials.

    def response(self, status, body, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def result(self, status, value):
        self.response(status, json.dumps(value).encode())

    def allowed_host(self):
        return self.headers.get("Host") == urlsplit(self.server.origin).netloc

    def do_GET(self):
        if not self.allowed_host():
            self.result(403, {"message": "Wrong host."})
            return
        files = {"/": (self.server.page, "text/html; charset=utf-8"),
                 "/style.css": (CSS, "text/css"), "/app.js": (JS, "text/javascript")}
        if self.path not in files:
            self.result(404, {"message": "Not found."})
            return
        body, content_type = files[self.path]
        self.response(200, body, content_type)

    def do_POST(self):
        if (not self.allowed_host() or self.headers.get("Origin") != self.server.origin
                or not secrets.compare_digest(self.headers.get("X-Setup-Token", ""), self.server.token)):
            self.result(403, {"message": "Open the setup link supplied by the local helper."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY or self.headers.get("Content-Type") != "application/json":
                raise CredentialError("Invalid request.")
            value = json.loads(self.rfile.read(length))
            if self.path == "/save":
                self.server.keychain.save(value)
                self.result(200, {"message": "Saved to Mac Keychain. Next, check unattended access."})
            elif self.path == "/check":
                self.server.keychain.read()
                self.result(200, {"message": "This process can access the login without an unlock. A fresh-process login test is still required."})
            elif self.path == "/copy":
                if not isinstance(value, dict) or value.get("field") not in ("username", "password"):
                    raise CredentialError("Choose a login field.")
                self.result(200, {"value": self.server.keychain.read()[value["field"]]})
            else:
                self.result(404, {"message": "Not found."})
        except CredentialError as exc:
            self.result(400, {"message": str(exc)})
        except (ValueError, UnicodeError):
            self.result(400, {"message": "Invalid request."})
        except Exception:
            self.result(500, {"message": "Local credential operation failed."})


def make_server(keychain, site, service, account, port=0):
    validate_scope(service, account, site)
    server = HTTPServer(("127.0.0.1", port), Handler)
    server.origin = f"http://127.0.0.1:{server.server_port}"
    server.token = secrets.token_urlsafe(32)
    server.keychain = keychain
    server.page = PAGE.replace(b'__SITE__', html.escape(site).encode()).replace(
        b'__SERVICE__', html.escape(service).encode()).replace(b'__ACCOUNT__', html.escape(account).encode())
    server.timeout = 1
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("serve", "check"))
    parser.add_argument("--service", required=True, help="Dedicated non-secret Keychain service identifier")
    parser.add_argument("--account", required=True, help="Non-secret item key, usually the website hostname")
    parser.add_argument("--site", required=True, help="Authorized HTTPS website origin")
    args = parser.parse_args()
    try:
        service, account, site = validate_scope(args.service, args.account, args.site)
        keychain = MacKeychain(service, account)
        if args.mode == "check":
            keychain.read()
            print("Dedicated website login is accessible without an interactive unlock.")
            return 0
        server = make_server(keychain, site, args.service, args.account)
        print(f"Local setup link: {server.origin}/#{server.token}", flush=True)
        print("Stop this helper with Ctrl-C after login setup/testing.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0
    except CredentialError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
