# CLI skills: research and verification

Research date: 2026-10-08. The user requested Codex, Cursor Agent, Claude Code,
Antigravity and OpenCode instructions, grouped under `skills/cli/` in the
repository and installed flat in every configured skill directory. YOLO execution
is within the requested workflow; each skill explains its own CLI's flag.

The five skills are independently written from installed-binary checks and
official documentation. Third-party skills were discovery/review material only;
no third-party bodies, scripts, installers or permission policies were imported.
This avoids carrying stale flags, host-specific wrappers, credentials or unrelated
automation into the user's machines.

## OMGSkills and online candidates

Searched OMGSkills for `codex`, `cursor`, `cursor-agent`, `claude cli`,
`antigravity` and `opencode`. Catalog ranking is not a substitute for source review.
The relevant records were discovery-only; source reviews below resolved GitHub
commits explicitly rather than running mutable catalog install commands.

| Tool | Candidate reviewed | Why it wasn't installed unchanged |
| --- | --- | --- |
| Codex | [skills-directory/skill-codex](https://github.com/skills-directory/skill-codex/blob/0cf3e4b6e801cae209fc27a50440b453b44af910/plugins/skill-codex/skills/codex/SKILL.md) | Uses absent `--full-auto`, suppresses stderr and claims no intermediate output; the current binary emits JSONL progress and needs diagnostics preserved. |
| Claude | [yu-iskw/coding-agent-skills](https://github.com/yu-iskw/coding-agent-skills/blob/ceb10d23cba617f34a21e13665579ba83d901c37/skills/claude-code-cli/SKILL.md) | Older model/permission assumptions, top-level `--sandbox` examples and extra approval rules don't fit the installed command or the user's workflow. |
| Cursor | [Dicklesworthstone's Cursor skill](https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations/blob/4d332440c34d7b077de8edc089bd06ec8d1d2f3a/skills/cursor/SKILL.md) | Documents the editor launcher rather than Agent CLI inference. Catalog `clawdbot/skills` and `zjh08177/agent-harness` candidates returned HTTP 404 at their repository API endpoints during review. |
| Antigravity | [SafeMantella CLI skill](https://github.com/SafeMantella/claude-code-agy-CLI-skill/blob/53b128fde5c6376894245447ce34e44f7a18d1b1/SKILL.md) | Host-specific paths and merged output examples, with insufficient current model/effort and terminal-envelope handling. |
| Antigravity | [Google's antigravity-support skill](https://github.com/google-gemini/gemini-cli/blob/56da16d54e9148ac9d763438a2294c805ace7207/packages/core/src/skills/builtin/antigravity-support/SKILL.md) | Primarily installation/migration guidance, not supervision of an already installed CLI. |
| OpenCode | [pcx-wave/opencode-skill](https://github.com/pcx-wave/opencode-skill/blob/7b06df5ae3318c52e74242467cde2071d4ea53f9/SKILL.md) | Depends on host wrappers/flag files and includes estimates of usage from edited lines; native CLI events and effective provider catalogs better meet this task. |

## Local checks before installation

All inference checks used temporary workspaces and a tiny prompt requesting
`CLI_SMOKE_OK` without tools. No quota was deliberately exhausted, no account was
changed, and no credentials were copied into the repository. CLI session metadata
may still be recorded by tools without an ephemeral option.

| Binary | Version | Verified outcome |
| --- | --- | --- |
| `codex` | 0.161.0 | App-server `model/list` and `account/rateLimits/read` succeeded. `gpt-6.1-sol`/`high` finished with exit 0, `turn.completed`, answer and usage. |
| `cursor-agent` | 2026.10.01-e373342 | Help advertises parameterized model IDs. Model listing and headless prompt returned exit 1, stderr authentication required, empty stdout. Account catalog and successful inference remain unverified. |
| `claude` | 2.1.294 | Stream control initialization returned model aliases, resolved IDs and per-model effort levels. Headless prompt failed authentication with exit 1 and `is_error: true`, despite `subtype: "success"`. Successful inference remains unverified. |
| `agy` | 1.3.1 | Model listing, JSON and streaming inference, and `/usage` succeeded. Invalid effort and conflicting suffix/effort failed with exit 1 plus structured ERROR before inference. Help says timeout default is unbounded, unlike the fetched guide; skills set it explicitly. |
| `opencode` | 1.18.35 | Model listing and loopback `/config/providers` returned model capabilities/variants. No OpenAI provider was configured. Invalid provider emitted an error event and exit 1. Default inference exceeded 55 seconds; explicit local `omlx/Qwen3.8-27B-4bit` exceeded 25 seconds, both after only a start event. Neither proves exhaustion. |

The Codex catalog offered `low`, `medium`, `high`, `xhigh`, `max`, `ultra` for
GPT-6.1 Sol. Claude initialization offered five efforts through `max` for Opus 5.5,
Sonnet 5.5, Haiku 5.5 and Fable 5.1. Antigravity's fetched slugs here used low,
medium and high (some families offered fewer). OpenCode's configured providers
had different per-model variant sets, and local Qwen entries had no variants.
These are dated observations, not a permanent cross-provider compatibility table.

## Caller contract

Each skill tells the invoker to preserve process exit, terminal event, errors,
usage, session identity and requested/resolved model/effort. Startup, partial text
and missing terminal output must not be treated as success. Usage means consumed
tokens, not remaining allowance. Account quota, short-lived rate limiting,
context/output caps, auth errors and deadline expiry have different remedies.
Unknown diagnostics remain unknown; partial edits are inspected before retries.

Packaging checks passed with the skill-creator validator and `gh skill publish .
--dry-run`. All five passed skillstrap's existing static scan, and an isolated
`gh skill install --from-local` check confirmed flat directories, flat reported
skill names and intact supporting references. The 46-test suite passed under sh
and dash, including nested-source selection and flat-target symlink preflight.

## Primary documentation

- Codex: [non-interactive mode](https://developers.openai.com/codex/noninteractive),
  [app-server](https://developers.openai.com/codex/app-server).
- Cursor: [parameters](https://cursor.com/docs/cli/reference/parameters),
  [output format](https://cursor.com/docs/cli/reference/output-format),
  [SDK model catalog](https://cursor.com/docs/sdk/typescript).
- Claude: [CLI reference](https://code.claude.com/docs/en/cli-reference),
  [models and efforts](https://code.claude.com/docs/en/model-config),
  [headless output](https://code.claude.com/docs/en/headless).
- Antigravity: [headless mode](https://antigravity.google/docs/cli/headless/),
  [CLI reference](https://antigravity.google/docs/cli/reference).
- OpenCode: [CLI](https://opencode.ai/docs/cli/), [models](https://opencode.ai/docs/models/),
  [server API](https://opencode.ai/docs/server/).

The installed help and observed protocol take precedence over stale examples.
Successful inference after Cursor/Claude login, long-running OpenCode inference,
and actual quota/context-limit envelopes remain future validation opportunities;
the skills explicitly describe these limits rather than presenting them as tested.
