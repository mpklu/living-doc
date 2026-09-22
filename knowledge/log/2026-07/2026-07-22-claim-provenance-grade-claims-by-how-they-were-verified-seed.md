## [2026-07-22] methodology | claim provenance — grade claims by how they were verified (seeded)

New optional pattern + tool, from the same field review that produced the
maintenance suite. Problem: AI agents write most articles, and their worst
failure mode is confident prose around an unverified inference — read as
fact months later, built upon, compounding. The field repo was already
tagging ad-hoc ("code-confirmed (path:line)", "verified on Beacon", "not
bench-tested"); this standardizes that practice into five inline tags —
`*(code: path:line)*` · `*(bench: date)*` · `*(field: incident)*` ·
`*(reported: who)*` · `*(inferred)*` — greppable by one regex, bound by
rules (load-bearing claims only; evidence required; no laundering
inferred→code without doing the verification; untagged claims inherit the
article's `status`).

Design: `concepts/methodology/claim-provenance.md` (self-demonstrating —
it tags its own claims). Tooling: `provenance-report` (coverage view flags
`load_bearing` articles with zero tags; `--worklist` emits every
inferred/reported claim in a load-bearing article — the generated input
for verification/refutation sweeps, per scripts-over-reasoning). Ties
planned: `thin → mature` promotion gated on tag coverage; adversarial
verification sweeps consume the worklist (both in ROADMAP). Adopter
surface kept minimal until field-validated: glossary entry + one pointer
in the overview's decision rule 4; guides/templates fold-in deferred.
