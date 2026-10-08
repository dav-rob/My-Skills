# Negative knowledge

What was tried: Marker-only detection of the bootstrap PATH block.
Why: Avoid duplicate `.zshrc` edits.
What happened: A marker with no export prevented repair; an existing export with
no marker was duplicated.
Conclusion: Check for the exact PATH export line instead.

What was tried: Audit functions sharing ordinary shell variables.
Why: Simple POSIX shell implementation.
What happened: Bulk static scanning reset the validator's failure status to PASS.
Conclusion: Isolate function variables with subshells and test combined failures.

What was tried: Uninstall path checks using home prefix and any `/skills/` segment.
Why: Permit user-scope installations from gh.
What happened: Traversal and parent symlinks could escape the intended location;
removing earlier rows before validating later rows caused partial deletion.
Conclusion: Allowlist parents, resolve them physically, and preflight all rows.

What was tried: Quietly skipping files over 1 MiB during the audit.
Why: Keep scans inexpensive.
What happened: Oversized suspicious files could receive PASS without being scanned.
Conclusion: Reject oversized files explicitly.

What was tried: Treating `gh --agent antigravity` installation as sufficient for
Antigravity 2.0.
Why: The target name appeared to cover Antigravity generally.
What happened: Skills existed under `.gemini/antigravity/skills` but were absent
from the app. Installing with `antigravity2.0` into `.gemini/config/skills` made
exact-address appear as Global in Settings → Customizations.
Conclusion: Use the surface-specific target and verify app discovery. The old
slash-command picker initially remained stale even after installation; the
Customizations screen showed the newly loaded skill.

What was tried: Treating local gh install selection as remote path selection.
Why: Verify the grouped CLI skills before publishing.
What happened: --from-local with skills/cli/cli-codex/SKILL.md was not found;
selecting cli-codex succeeded. Remote pinned exact-path selection also succeeded,
but its listing identity was scoped rather than flat.
Conclusion: Preserve exact remote path selection for audited installs and handle
scope metadata in uninstall; don't switch to local copying to hide the namespace.

What was tried: Short OpenCode smoke deadlines and interpreting startup-only output.
Why: Bound CLI validation cost and duration.
What happened: Default/free and local requests emitted only start events within
short deadlines. Explicit discovered free models later completed, and local
Qwen3.6 needed a longer deadline. Qwen3.8 still missed 90 seconds.
Conclusion: Refresh discovery, pin a selected model, and distinguish timeout from
authentication/quota errors. Start events never establish success.
