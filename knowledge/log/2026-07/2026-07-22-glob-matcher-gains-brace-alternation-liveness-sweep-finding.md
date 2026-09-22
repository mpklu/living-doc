## [2026-07-22] tooling | glob matcher gains brace alternation (liveness-sweep finding)

The field repo's full liveness sweep (26 product-repo roots) surfaced a
matcher gap, not just article rot: articles naturally write
`Models/{Allergy,Medication}.swift`, and `_glob_to_regex` treated the
braces as literals — those affects entries had NEVER matched anything
in drift-check. `_expand_braces` now expands alternation (recursive)
before translation; both drift-check matching and check-affects
liveness consume it. Fixtured both ways (alive brace glob silent in the
linter; a change to a brace-matched file flags in drift-check).
