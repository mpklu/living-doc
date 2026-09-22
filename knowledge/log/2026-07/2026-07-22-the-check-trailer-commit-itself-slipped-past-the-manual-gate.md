## [2026-07-22] meta | the check-trailer commit itself slipped past the manual gate

Honest process note: the check-trailer commit printed a drift-check
violation (`templates/hooks/**` → `tooling/drift-check.md`) and was
committed anyway — this repo's gate is still MANUAL (no installed
pre-commit hook), and manual gates get skipped under momentum. Two
fixes: the mapping (hooks README now documents the whole tool family →
`templates/hooks/**` added to maintenance-tools.md as shared ownership),
and the irony is noted — the repo that ships `pre-commit-gate --install`
hasn't installed one itself. Deliberately left manual for now (this repo
is edited rarely and reviewed closely), but the failure mode is now on
record: it happened on the very commit that shipped the cross-repo
enforcement hook.
