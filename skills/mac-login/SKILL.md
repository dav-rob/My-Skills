---
name: mac-login
description: >-
  Enable unattended credential access for website and browser-based tool logins
  on macOS when a password manager requires interactive authentication. Use a
  local setup webapp and dedicated Apple Keychain item to keep username/password
  values out of agent context. Not for unlocking macOS or bypassing MFA/CAPTCHA.
---

# Mac Login

Use a dedicated Apple Keychain item when a website login must run without someone
present to authenticate a password manager. The user enters the username/password
once in a local setup webapp; later runs retrieve that item without an interactive
unlock and copy each field for normal sign-in.

**Start directly with this workflow.** A password manager that requires an
interactive unlock is unsuitable for unattended runs. Do not spend time testing
autofill, attempting to unlock the manager or exploring its vault. This workflow
stores a separate, explicitly authorized credential; it leaves the password
manager's protections intact.

The helper supports username/password websites, including browser-based sign-in
for other tools. Other credential types and native-only login flows need their
own integration. Non-interactive credential retrieval has been demonstrated;
screen-locked browser operation and access after reboot are separate checks.

## 1. Choose the item and set it up once

Use the bundled [scripts/credentials.py](scripts/credentials.py), which calls
macOS Security.framework directly and needs no extra Python dependencies.
Choose a dedicated service name, a non-secret account key (usually the hostname)
and the authorized HTTPS website origin. `--account` identifies the Keychain
item; it is not the user's email. Reuse the same Python executable for setup and
scheduled runs: a different interpreter identity may require a new access grant.

Resolve the helper from this skill's directory. For example:

```bash
python3 /absolute/path/to/mac-login/scripts/credentials.py serve \
  --service com.example.mac-login.task --account example.com \
  --site https://example.com
```

Open the printed `http://127.0.0.1:<random-port>/#<token>` link with the available
Computer Use tool. Show the page to the user, who enters the login and clicks
**Save login to Mac Keychain**. Read only `#status` to verify saving; do not read
or capture the credential inputs. Saving requires the user's explicit action.
If the authorized item already exists, reuse it instead of repeating setup.
The helper refuses overwrites; replacements belong in Keychain Access with the
user's direction.

The temporary webapp checks the exact loopback Host, Origin and random token,
suppresses request logs and uses no-store/CSP headers. It removes the fragment
from the address bar. A refresh loses its in-memory token; reopen the original
link or restart the helper. Do not persist that token link in files or prompts.

## 2. Verify access without a human

Run `check` in a **new process**, using the same Python and item scope:

```bash
python3 /absolute/path/to/mac-login/scripts/credentials.py check \
  --service com.example.mac-login.task --account example.com \
  --site https://example.com
```

This prints availability only. Reads suppress interactive Keychain dialogs for
that process and restore its previous interaction policy. An unavailable item
fails instead of asking for a morning unlock. Resolve a failure while the user
is present; do not weaken global Keychain or password-manager protections.

## 3. Complete and verify normal sign-in

Use the available Computer Use tool. When commissioning unattended login,
explicitly sign out if already signed in and prove a fresh sign-in. Match the
destination to the authorized site before pasting credentials.

1. Open the helper and click **Copy username**; verify `#status`.
2. Select the website in the native browser, focus its observed username field
   and paste from the OS clipboard. Continue to the password step as required.
3. Click **Copy password**, focus the correct password field and paste. Submit
   sign-in and verify the authenticated task page without reading secret fields.
4. Click **Clear clipboard**, close temporary helper tabs and stop the helper
   process started for this attempt.

For Chrome, native `app.pressKey("super+v")` worked. Browser-tab
`pressKey(null, "super+v")` used a separate virtual clipboard and failed with
“no data to paste”. Select and verify the native active tab/focused field from
fresh UI state; background browser actions may not select that tab. For other
browsers, use their supported native OS-clipboard paste operation.

Never read the clipboard, a password input value or the `/copy` response into
agent context. Credentials temporarily exist in local memory and the OS
clipboard; this bridge keeps them out of chat, tool output, logs, plaintext
files and process arguments. Do not replace it with secret-bearing shell commands.

## 4. Record the operating limits

Record the non-secret item scope, Python/helper paths and verified paste method
for later runs. Report fresh-process access and fresh sign-in separately. For
scheduled work, verify the actual intended conditions before claiming reliability:
Keychain availability does not prove browser control works with the screen locked,
and an asleep or logged-out Mac differs from a screen-locked, awake session.

Stored credentials grant normal account capabilities; follow only the user's
authorized task, including any read-only constraint. Stop with a specific failure
if MFA, CAPTCHA, an interactive unlock or a security interstitial requires a
human. This skill does not authorize account changes or scheduling by itself.
