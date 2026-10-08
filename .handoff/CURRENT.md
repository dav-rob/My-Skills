# Current

Five CLI skills are prepared under `skills/cli/`: cli-codex, cli-cursor,
cli-claude, cli-antigravity and cli-opencode. They were researched through
OMGSkills and official sources, independently written, and checked against
installed binaries. They cover native model/effort discovery, authorized YOLO
options, deadlines and caller-visible completion/errors/usage. See
`docs/CLI-SKILLS.md` for pinned candidate sources and verification limits.

Implementation is pushed as `3c9c00e`, `6ea908e` and `5e51d21`. The source grouping
installs flat; all five are installed in all eight configured paths (40 copies).
gh reports remote scope/name identities from source metadata;
uninstall accepts a single safe source scope while retaining exact target/parent
checks. The local skillstrap command was updated by curl bootstrap and matches
the repository. 49 offline tests passed under sh and dash; format/static checks,
nested local/remote packaging and live flat-name uninstall also passed.

Codex (GPT-6.1 Sol/high), Antigravity (Gemini 3.8 Flash/high), two discovered
OpenCode free models at low effort, and oMLX Qwen 3.6 completed smoke requests.
Qwen 3.8 didn't finish within 90 seconds. Cursor and Claude need authentication;
the user was given login commands and offered to authenticate them. Their
successful inference checks can be completed when the user confirms login.
Never claim real quota/context exhaustion was induced or verified.

Configurable install paths remain as implemented in `29424e8`: eight defaults
including scheduled jobs, saved active-list configuration, explicit selection,
audited commit pins, and complete destination preflight. Removing a path leaves
its content in place. Bootstrap installs the command only. The vision remains
any GitHub source and every compatible tool, with safety and security foremost.
Static audits remain incomplete and sequential installs may partially succeed.
