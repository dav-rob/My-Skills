# Current

`mac-login` is now in `skills/mac-login/`, implemented and pushed as `b9abc7a`.
It documents the 7 October Rightmove signed-out login proof, dedicated Keychain
setup, fresh-process retrieval without dialogs and the native Chrome OS clipboard
paste requirement. Its bundled Python helper supports explicit service/account/
HTTPS-site parameters and refuses item overwrite. No credentials are in the skill.
The generalized helper's readonly check succeeded against the existing owner
Rightmove item using the established Python executable; no new item/login run
was needed for this packaging task. Skill format validation passes.

The vision is distribution from any GitHub repository to every compatible tool,
with safety and security as the primary design goals. The current seven targets
and conservative static audit are implementation limits to improve, not limits
on the project's intended scope. No runtime expansion was made by this vision correction.

Antigravity 2.0 support is complete on `main`: seven install targets, including
`antigravity2.0`, and uninstall support for `.gemini/config/skills`.

All 33 offline tests pass under sh and dash: the 24 existing distribution tests
and nine scoped credential-helper checks using fake secrets/disposable loopback
ports. Shell syntax and staged diff checks also pass. The new skill was created
in the requested repository; installed skill copies were not updated by this task.

The user's installed command was updated from GitHub and used to install
exact-address for all seven targets. Antigravity 2.18.1 visibly lists it as Global
in Settings → Customizations. The legacy linker has been removed.

No outstanding requested work. Preserve explicit selection, compact audits,
pinned installs and conservative uninstall. Future app support should verify
actual app discovery as well as CLI placement.
