# Antigravity conversation follow-up

Read this for web handoff or resuming a conversation that used `--json-schema`.
The checks below used agy 1.3.3 on macOS on 2026-10-12.

## Temporary web access

In the original working directory and CLI profile, resume the exact saved UUID
interactively with remote access:

```sh
agy --conversation "$conversation_id" --model "$model_slug" --effort "$effort" \
  --remote-control
```

Use the actual URL printed by this instance. The tunnel lasts only while this
interactive CLI process runs; exiting it removes that temporary instance. Web
access requires the owner's signed-in Google account. A desktop/editor remote
instance can be separate from the CLI instance and may not show its history.
Don't substitute an existing editor link or guess an instance ID from a UUID.

## Persistent web access

For authorized ongoing remote access, inspect the existing service first:

```sh
agy remote-control status
agy remote-control start --help
```

The official service can be registered with:

```sh
agy remote-control start --name "my-workstation"
```

This installs a background OS service (a login LaunchAgent on macOS), and allows
the signed-in CLI account to access conversations and start tasks remotely.
Enable it when the user's request covers persistent access; don't infer that
authorization from a request for a headless answer alone. Reuse existing access
when suitable. Check `status`, select the verified CLI instance in the remote
dashboard, and open the exact conversation. Preserve the URL obtained there.
Do not assume it works while the host is asleep or logged out. On macOS it starts
at login; other platforms have different service lifecycles.

If persistent access is being removed within the user's request, the official
command is `agy remote-control stop`; it unregisters the service. Exiting a
temporary CLI session does not stop the background daemon. Don't stop unrelated
editor instances or change network exposure to repair a conversation link.

For email/report handoff, include the verified web conversation URL and the exact
CLI resume command with the original working directory. Quote shell arguments
properly. Check history visibility without sending another model prompt when a
read-only inspection suffices; a web follow-up executes on the host and may act.

## Structured output after resume

In one resumed schema-based conversation, terminal `response` contained the new
corrected answer while `structured_output` still contained the earlier report.
This is one observation, not a reproduced general rule. Preserve both fields and
verify that structured data reflects the current turn before using it downstream.
If they disagree, report the inconsistency rather than presenting old data as the
new result. Validate any JSON parsed from the current response against the intended
schema; don't silently replace structured output with arbitrary prose.

For readable web discussion, requesting ordinary Markdown produced a visible
answer after an earlier report-tool response showed only a completion summary.
Choose presentation for the destination while retaining validated structured data
for machine consumers.

## Sources and limits

[Official Remote Control documentation](https://antigravity.google/docs/remote-control/)
and [headless mode](https://antigravity.google/docs/cli/headless/).
Exact-ID CLI resume remembered prior context in a fresh process. Temporary web
access and the official persistent service both showed the intended CLI history
and accepted a follow-up; persistent web access worked after the temporary process
exited. Reboot/logout recovery and locked-screen GUI tools were not tested.
