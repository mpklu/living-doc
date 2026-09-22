## [2026-07-22] methodology | narrow local-vs-pr-enforcement's affects glob

The claim-provenance commit was (correctly) flagged by our own drift
check: `local-vs-pr-enforcement.md` claimed `actions/drift-check/**`
from when that dir held only enforcement code — the maintenance suite
now co-hosted there belongs to `tooling/maintenance-tools.md`. Narrowed
to the enforcement files per the checker's own "fix the pattern"
resolution. (The suite commit a day earlier passed only coincidentally —
the description migration happened to touch this article. The mechanism
works; broad `**` globs on shared directories age badly.)
