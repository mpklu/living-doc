## [2026-07-22] tooling | check-trailer — cross-repo same-task enforcement + v0.2.0 tagged

The last big enforcement gap: drift-check guards the knowledge repo, but
the same-task rule's other half lives in product repos it cannot see —
the `Knowledge:` trailer convention rode on discipline alone.
`check-trailer` closes it: a commit-msg hook installed per product repo
matches staged paths against the knowledge repo's affects globs (full
matcher: `**`, brace alternation, repo-basename-prefixed candidates;
`external:` entries match by repo name and map the whole repo to their
article) and blocks trailer-less mapped commits with the expected
article list and a paste-ready fix. `no knowledge impact: <reason>`
satisfies deliberately-doc-irrelevant commits — same convention as the
before-commit checklist. Helpful-not-hostile: any non-empty trailer
satisfies v1, `--warn-only` for rollout, and the missing-CI-net behind
`--no-verify` in product repos is documented as the trade-off rather
than hidden. Eight-case fixtured (block/trailer/no-impact/unmapped/
brace+prefix/external/warn-only/install).

Timing is deliberate: yesterday's affects hygiene sweep (linter + 29
dead globs fixed + brace support) made the mapping trustworthy enough
to enforce against — building this hook first would have been
false-positive hell. With it shipped, **v0.2.0 is tagged**: the
maintenance suite (8 tools), four methodology patterns (facts register,
claim provenance, what-cache/why-asset, scripts-over-reasoning), the
enforcement wiring patterns, and the field-driven matcher fixes — the
whole first re-adoption cycle, pinable.
