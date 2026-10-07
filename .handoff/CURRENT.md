# Current

`mac-login` is in `skills/mac-login/`, initially implemented as `b9abc7a` and
refocused/generalized in `81dcbc4`. It leads directly to a local setup webapp and
dedicated Apple Keychain item when a password manager requires interactive
authentication; agents must not spend time exploring autofill or unlocking the
manager. Personal/site-specific instructions and test fixtures were removed.
The existing parameterized helper is unchanged: explicit service/account/HTTPS
origin, refusal to overwrite, fresh-process checks without dialogs and native OS
clipboard paste. Browser-based tool logins fit this workflow; native-only flows
need separate integration. Screen-lock/reboot operation is not established by a
credential-access check. Nine isolated helper checks and skill format validation
pass for this revision; no real credentials or browser sessions were accessed.

The vision is distribution from any GitHub repository to every compatible tool,
with safety and security as the primary design goals. The current seven targets
and conservative static audit are implementation limits to improve, not limits
on the project's intended scope. No runtime expansion was made by this vision correction.

Antigravity 2.0 support is complete on `main`: seven install targets, including
`antigravity2.0`, and uninstall support for `.gemini/config/skills`.

The earlier full run passed 33 offline tests under sh and dash: 24 distribution tests
and nine scoped credential-helper checks using fake secrets/disposable loopback
ports. Shell syntax and staged diff checks also pass. The new skill was created
in the requested repository; installed skill copies were not updated by this task.

The user's installed command was updated from GitHub and used to install
exact-address for all seven targets. Antigravity 2.18.1 visibly lists it as Global
in Settings → Customizations. The legacy linker has been removed.

No outstanding requested work. Preserve explicit selection, compact audits,
pinned installs and conservative uninstall. Future app support should verify
actual app discovery as well as CLI placement.
