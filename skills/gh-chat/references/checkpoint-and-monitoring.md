# Checkpoint and monitoring reference (provisional)

Use this when creating a sustained PR conversation or recovering it. Adapt the layout to the environment; no runner or fixed API is shipped with this first version.

## Minimal ledger

Use atomic replacement in the same directory, and keep one writer or a lock. The schema below illustrates distinct states rather than prescribing an implementation. Store large logs/reproductions separately and link them by path/hash. Keep the ledger private or ignored unless the user requests a reviewed, sanitised handoff in Git.

```json
{
  "schema_version": 1,
  "status": "provisional",
  "pr_url": "https://github.com/OWNER/REPO/pull/NUMBER",
  "identity": {"self": "[codex]", "peer": "[claude]"},
  "authority": {
    "human_instruction_ref": "chat message or other trusted approval reference",
    "actions": ["review", "comment", "monitor"],
    "stop_when": "PR closed or merged"
  },
  "heads": {"observed": "sha", "reviewed": "sha", "approved": null},
  "messages": {
    "service-comment-id": {
      "body_hash": "sha256",
      "state": "needs_reply",
      "request": "Is this revision approved, or are checks outstanding?",
      "reply_id": null
    }
  },
  "findings": {
    "F1": {
      "state": "awaiting_fix",
      "comment_url": "https://github.com/OWNER/REPO/pull/NUMBER#issuecomment-ID",
      "reproduced_head": "sha",
      "verified_head": null,
      "evidence": ["reproduction.json"]
    }
  },
  "outbox": [{
    "operation_id": "uuid",
    "target": "PR conversation",
    "reply_to": "service-comment-id",
    "body": "[codex] ... <!-- gh-chat:uuid -->",
    "state": "prepared",
    "remote_id": null
  }],
  "monitor": {
    "id": "native-scheduler-id",
    "kind": "same-chat heartbeat",
    "cadence": "one minute",
    "notification_policy": "effective value or unknown",
    "last_successful_poll": "UTC timestamp",
    "last_attempt": "UTC timestamp",
    "last_error": null
  },
  "next_action": "Reconcile the pending comment, then verify F1 at the current head"
}
```

Keep initial human authority distinct from peer comments and review approval. Include merge/integration in `actions` only when the human granted it. A delivery status belongs in the outbox even if the main read watermark has advanced. Comment edits can reopen `needs_reply`; a changed head can invalidate `approved`.

## Wake-up procedure

1. Load the PR identity, authority, stop condition and ledger. Verify any previous monitor is still the intended one; do not duplicate it.
2. Read current remote state and reconcile prepared/unknown outbox entries by marker/ID before issuing writes. A posted comment with an unrecorded response should be recorded, not reposted.
3. Read new **and edited** comments/reviews plus still-pending earlier requests. Identify your own operations from recorded IDs/markers; an identical GitHub login does not make every message yours.
4. Check whether the head changed. Verify affected fixes at the new exact head; avoid declaring the whole PR approved on tests of an older revision.
5. Write a useful signed reply or perform the next already-authorised action, then save the result. Leave a durable next action if waiting for the peer or a human.
6. If the stated stopping condition is satisfied, record the outcome and stop the monitor. Otherwise yield without a routine human update; confirm notification suppression through the actual scheduler settings, not response wording.

## Scheduler and notification checks

Discover the native tools and their current schemas. Same-chat schedules preserve conversation context but still require a durable ledger. Existing schedules may have been manually edited; creation arguments alone do not prove their effective settings. Save the settings that can actually be read back.

In the Codex app tool surface observed in October 2026, recurring same-chat work used a heartbeat automation and exposed `notificationPolicy: "failed_runs_only"` as an optional field. This is a dated capability observation, not a portable API contract. Re-read the available tool before using it. That policy suppresses normal completion alerts; it does not implement meaningful-success-only alerts, and failed/quota-limited runs may still notify. Keep preferences out of the prompt when the tool has dedicated fields. Do not mute unrelated work or launch a test that sends a stream of alerts.

A successful check with no assistant text can still complete a turn. A long active turn can reduce completion events but is not durable on its own and can consume allowance until it stops. Prefer verified notification controls over deliberately keeping a turn alive to avoid alerts.

## Recovery evidence and limits

Two real PR conversations in October 2026 used minute heartbeats, durable ledgers and quiet-on-unchanged prompts, without explicit notification overrides. One stayed in a continuous working turn, then encountered account usage-limit failures until a later scheduled attempt resumed and completed integration. The other repeatedly completed successful empty turns while the owner received minute-by-minute tablet alerts. The local turn events support the different execution patterns; they do not establish the exact mobile push-delivery cause or a universal notification rule.

The reusable practices are saved progress, an independently persistent wake-up mechanism, reconciliation before retry, and explicit notification controls. Do not intentionally exhaust quota to test them. Host shutdown, logout, revoked credentials, a disabled schedule and missed external events need separate verification.

## Behavioural checks for future iterations

Use isolated/mock artifacts or already captured history; no live write or quota exhaustion is needed to walk these cases:

- **Shared account:** a new `[claude]` question has the same login as your last `[codex]` reply. Keep it actionable and answer it.
- **Seen but unanswered:** all findings are fixed, and an observed comment asks for explicit approval. State approval or remaining checks; do not silently advance the watermark.
- **Edited request:** the same comment ID gains a new question. Its body hash changes and reopens the action.
- **Lost post response:** the outbox says prepared, but the remote marker already exists. Record its ID and avoid duplication.
- **Quota gap:** several wake-ups fail; the first recovered run reads the latest head/discussion and pending outbox before continuing. Do not claim polling coverage during the gap.
- **Quiet unchanged run:** no findings changed and no request is pending. No new GitHub/human status message is needed; a normal completion may nevertheless alert unless actual notification controls suppress it.
- **New head after approval:** preserve the old approval evidence, review the delta, and update approval only after necessary verification.
- **Closure:** distinguish merged from closed unmerged, record any unresolved findings, and stop the recorded schedule exactly once.
