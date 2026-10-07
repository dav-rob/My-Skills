---
name: mac-login
description: >-
  Set up and verify unattended website login on macOS with a dedicated Mac
  Keychain item and a local clipboard bridge when browser saved-password access
  is unavailable. Use for existing website credentials and repeatable browser
  sign-in; not macOS account login, password changes or bypassing MFA/CAPTCHA.
---

# Mac Login

Enable an authorized website sign-in without putting credential values in chat,
tool output, prompts, files or process arguments. This is the fallback proven
with Rightmove on David's Mac on 7 October 2026: a separate Python process could
retrieve the dedicated Keychain item without an unlock, and Chrome completed
login from an explicitly signed-out state. It does not establish access while
the Mac/Keychain is locked or after a reboot.

## Choose the credential path

Use an available approved password-manager/autofill workflow when it works.
Imported passwords alone do not prove the agent can invoke autofill unattended.
Inspect the actual available browser capabilities and signed-in state; do not
assume either. Stop exploring the manager when its usable interface is unavailable
and offer the scoped Keychain setup below. Do not extract browser vault databases
or change global authentication/unlock policy.

The skill authorizes no new destination or website action. Establish the task's
target and permitted operations from the user's instructions; reuse existing
authorization rather than asking again on every sign-in. For a new Keychain item, have the
user enter and explicitly save the login through the local setup form; never
silently copy credentials into persistent storage. Existing stored credentials
can be reused only for their authorized task/site. A login password grants normal
account capabilities; a read-only task remains an agent behavior constraint.

## Set up a dedicated Keychain item

Use the bundled [scripts/credentials.py](scripts/credentials.py). It uses macOS
Security.framework directly, has no extra Python dependency, and accesses only
the specified generic service/account item. Choose a dedicated stable service
name and a non-secret account key such as the website hostname. `--account` is
the storage key, not the person's email. Use the same Python executable for setup
and scheduled runs; changing interpreter identity may require a new access grant.

For the already-established Rightmove credential, the exact tuple is:

```text
service: com.davrob.auction-properties.rightmove-sync
account: rightmove.co.uk
site: https://www.rightmove.co.uk
Python: /Users/davidroberts/projects/quick-scripts/auction-properties/.venv/bin/python3
```

Do not recreate or replace that item when it is already usable. For another
task/site, choose its own service/account rather than reusing this example.
Resolve the helper path from the loaded skill's directory; do not assume the
skill was installed at the repository checkout path.

Start the helper using the chosen Python and explicit non-secret scope:

```bash
python3 /absolute/path/to/mac-login/scripts/credentials.py serve \
  --service com.example.mac-login.task --account example.com \
  --site https://example.com
```

Open the printed `http://127.0.0.1:<random-port>/#<token>` link in Chrome using
the available Computer Use tool. Show/mark the page for user handoff. The user
enters their username/password there and clicks **Save login to Mac Keychain**.
Read only `#status` to verify saving; do not capture inputs while they are typing.
The helper refuses to overwrite an existing item. Replacement/removal belongs
in Keychain Access with the user's direction.

The helper accepts credential operations only with the exact loopback Host,
Origin and random token. It suppresses request logging and uses no-store/CSP
headers. The page removes the fragment from the address bar; refresh loses the
in-memory token. Reopen the originally printed link or start a fresh helper,
instead of loosening checks. Do not persist the link token in Git or task prompts.

## Prove unattended retrieval and fresh login

Run `check` in a **new process** with the same scope and Python executable:

```bash
python3 /absolute/path/to/mac-login/scripts/credentials.py check \
  --service com.example.mac-login.task --account example.com \
  --site https://example.com
```

This prints availability only. Reads temporarily suppress interactive Keychain
dialogs for that process and restore its previous interaction policy. A locked
item or approval requirement produces failure, not a morning unlock request.
If it fails, resolve the specific access issue with the user present; do not
disable protections or promise unattended operation based on the setup process.

Use Computer Use for the website login. Inspect authentication state first; when
commissioning unattended access, explicitly sign out if needed and prove a fresh
sign-in. Match the actual destination to the user's authorized site before
pasting anything. For Chrome on the tested Mac:

1. Start/open the local helper and click **Copy username**. Verify `#status`.
2. Select the website tab in the native Google Chrome app from a fresh AX state,
   focus its observed username/email field, and use native
   `app.pressKey("super+v")`. Continue to the password step as required.
3. Click the helper's **Copy password**, focus the observed password field in
   the correct Chrome tab, and use the same native paste. Submit normal sign-in.
4. Verify the authenticated account/task page without reading secret fields.
   Click **Clear clipboard**, close temporary helper tabs and stop only the
   helper process started for this attempt.

**Tested trap:** the browser-tab `pressKey(null, "super+v")` path used a separate
virtual clipboard and failed with “no data to paste”, despite the helper's
successful OS clipboard write. Native Chrome `pressKey("super+v")` worked.
Native app actions affect its active tab; background browser actions may not
select that tab. Verify the native active tab/focused field rather than pasting
into whichever app happens to be foreground. Other environments may have
different clipboard routing; inspect supported APIs before choosing a method.

Never read the clipboard, a password input value or the `/copy` response into
tool results. Clipboard-copy necessarily puts credentials in local memory and
the OS clipboard; it does not print them or save plaintext files. Do not use
shell `security add-generic-password -w <password>` or a shell pipe to expose/transfer values.

## Carry the proof into recurring work

Only mark unattended login verified after both the new-process check and the
fresh website sign-in pass. When setting up a user-requested recurring task,
keep its initial setup paused until that proof; use the scheduler's supported
tool to update the authorized task. Record the
non-secret service/account tuple, Python/helper paths and successful method,
without credential values or transient token URLs. The Mac must be available
with the agent app running; Keychain/site prompts can still interrupt later runs.

Do not turn a requested read-only task into website changes, credential rotation,
manager installation, account recovery or an unrelated schedule. Stop with a
specific failure for MFA/CAPTCHA, security interstitials, wrong account or an
interactive unlock; follow the available tool's handoff/confirmation rules.

Report whether fresh login worked, whether human interaction was needed and
what remains blocked. The reference Rightmove run scanned 109 favourites and
committed five new properties; importing properties is separate from this
login skill and requires the task's own authorization and duplicate guards.
