# Handoff — local model dashboard, 18 November 2026

## Current objective

Host a very lightweight local website summarizing model-use behavior and current
recommendations, maintained by the existing weekly background process.

## What was done

Pushed `32e3c5c`: Python standard-library server and a buildless HTML/CSS template
under `dashboard/`, a macOS user-service installer, 37 dashboard tests, README
operation commands and the model-use maintenance reference's dashboard checks.
The server reads canonical `skills/model-use/SKILL.md` and
`skills/model-use/references/models.md` on each request. No duplicated model IDs,
request-time model calls, external assets, write endpoints or directory serving.
Only home/index and health routes are served; unknown hosts are rejected and
markdown content is escaped, with only http/https links permitted.

Used model-use for this task: Sonnet 5.5/high through Claude built the server,
template and initial tests; the manager reviewed/integrated it, corrected the
assessment-age inference, decoupled test fixtures from weekly recommendation
changes and wired hosting/maintenance. Local rotation/session state is in
`.model-use/state.json`, excluded through this checkout's Git info/exclude.
The next Codex-manager worker slot is Hydrogen. The worker completed successfully.

## Current state

The site is running at `http://127.0.0.1:48173/`, on loopback only. Service label:
`com.dav-rob.model-use-dashboard`. Its plist is in the user's Library/LaunchAgents;
logs are in Library/Logs/model-use-dashboard. Run
`python3 dashboard/install_service.py` after moving the checkout or changing
server code. Model-note/template edits appear on refresh without restart.
README has status/stop commands. The service is intended to run while this Mac
is awake and the user is logged in; a real logout/reboot was not performed.

Updated the existing automation `weekly-model-and-cli-skill-maintenance` through
the native tool. It retains its project, Monday 09:00 schedule, local execution,
`gpt-6.1-sol` and `xhigh`. Its prompt and maintained procedure now check `/healthz`
and the home page even after no-change reviews, verify source/date/model
consistency and repair only this service when needed. No duplicate automation.
A completed scheduled run has not yet been observed.

## Verification

- 86 tests passed (49 existing plus 37 dashboard). After making test examples
  independent of current recommendations, all 37 passed with warnings as errors.
- Coverage includes live markdown edits without restart, escaped hostile input,
  safe links, source failure/recovery, generic errors, blocked arbitrary paths,
  Host validation, read-only methods, security headers and CLI process cleanup.
- Skill-creator validation, relative/reference checks as applicable, format
  publish dry-run and diff checks passed. Existing recommended-license and tag
  protection warnings remain.
- Home and health return 200. Live recommendations/assessment date match source.
  Browser UI was inspected through the Sites local workflow; its tab was marked
  as a deliverable. No separate device-sized viewport test was performed.
- The loaded service recovered after SIGTERM via its own launchctl target.
  lsof confirmed only 127.0.0.1:48173. Reinstallation of the existing service passed
  after adding bounded retries for launchd's transient post-bootout error 5.

## Installation

The model-use maintenance reference passed the remote format/static audit and
was reinstalled in all eight paths at `32e3c5c56e8b685add7d10e30ff948d7dcae5bff`.
All 32 files, normalized bodies, reference/UI bytes, flat names/paths and exact
commit/tree metadata were verified. Only model-use was selected for installation;
the web service reads the checkout directly.

## Problems / blockers

None known for the running page. The first service reinstall exposed a launchd
release/bootstrap race, which was fixed and rechecked. Assessment age deliberately
does not claim a missed review: a healthy no-change weekly review leaves its date
unchanged. Do not invent live subscription allowances.

## Files currently being worked on

None. The service and installed maintenance reference are verified; only this
separate handoff commit remains to be pushed.

## Relevant recent commits

- `32e3c5c`: local dashboard, tests, service installer and maintenance procedure.
- `3f48f67`: original model-use installation verification.
- `5475424`: round-robin policy and starting recommendations.

## Immediate next steps

Delivery is complete; this handoff is the separate follow-up. Subsequent weekly
reviews read the maintained procedure. No new model research or changes to the
round-robin choices were required here. Keep the site local and read-only.

## Things not to do / re-investigate

Do not use a generic directory server for this repository, infer live allowance
or missed reviews from the assessment date, or duplicate recommendations in page
code. Leave the service running; temporary test servers are separately reaped.
