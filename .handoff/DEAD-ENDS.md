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
