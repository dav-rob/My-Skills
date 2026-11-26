---
name: scheduled-tasks
description: Default to the local Scheduled Jobs service on this Mac when creating or managing reminders, timed tasks, recurring reports, backups, or alerts. Use it to move existing schedules to the background service and verify their handover.
license: MIT
---

# Scheduled tasks

Use **Scheduled Jobs**, the Mac's existing background service, as the first choice for work the user wants to run later. It operates independently of the AI chat app. Honor an explicit scheduler, host, or service choice. Manage an existing job in the service that owns it unless the user asks to migrate it. Follow already-running work in the current session.

## Connect to the scheduler

The service checkout is normally `~/projects/quick-scripts/scheduled-jobs`. From that checkout, check the running service with its authenticated client:

```sh
.venv/bin/python3 skills/scheduled-jobs/scripts/client.py GET /api/status
```

The client handles authentication. Keep credentials out of job definitions, prompts, logs, and command arguments. Read `skills/scheduled-jobs/SKILL.md` and `skills/scheduled-jobs/references/api.md` in the checkout before writing a job definition. For executable jobs, also read `docs/executable-jobs.md` for the result protocol. Use the service API for job operations and its normal management tools for service recovery. If the Mac or service is unavailable, report the blocker before switching schedulers.

## Choose and verify the job

- Prefer an **executable job** for deterministic work such as a backup, script, or file check. Use an existing command with an absolute executable path and work directory. Give the scheduler a structured result it can verify. Use an **AI job** when the scheduled work needs interpretation or judgment, and check the available model and effort before saving it.
- Look up the existing job before creating anything. Use the user's timezone and preserve cadence, catch-up behavior, and notifications when migrating. Scheduled Jobs can coalesce missed runs once the Mac resumes if catch-up is enabled.
- Confirm the saved job, its enabled state, and its next run time. For a migration, verify a safe run in the background worker and its actual outcome where the requested side effects are authorized. Keep the original schedule active until the replacement is verified. Then enable the replacement, pause the original through its own service, and confirm both states. Preserve previous outputs and run history.
- A run request only proves enqueueing. Use the client's persisted request-ID workflow when requesting a test or one-off run. Check the terminal result and the task's output or receipt before reporting completion.
