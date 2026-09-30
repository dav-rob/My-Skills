# Current

The requested CLI reliability checks and fixes are complete on `main`.
All 24 offline regression tests pass under `/bin/sh` and `/bin/dash`.
Live bootstrap, dry runs, named/bulk installs and legacy-name removal passed in
temporary homes with GitHub CLI 2.101.0. No known blockers.

Future changes should preserve explicit selection, concise audits, pinned
installation and conservative uninstall. A semantic auditor is a possible later
feature; no such implementation has been requested.
