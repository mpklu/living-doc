## [2026-07-22] tooling | provenance-report: evidence keywords require ':' (wild false positive)

Dogfooding the corroboration fix on the field repo's 98-article corpus
surfaced a prose look-alike: `**(code × feeschedule × provider)**`
contains the substring `*(code …)*` and the space-tolerant lookahead
counted it as a code tag. Evidence-bearing keywords
(code/bench/field/reported) now require a following ':' — the
convention's actual shape — while `inferred` keeps its bare
(`*(inferred)*`) and space-continued (`*(inferred from X)*`) forms.
Fixture gained both trap cases. Two scanner refinements from one
field corpus in one day: real-corpus dogfood is the test suite no
fixture anticipates.
