## [2026-07-22] tooling | check-dates — the stale-date flagger (time-bombed prose)

Generalizes the field incident that opened the whole review: a hard
vendor retirement date sat FUTURE-tense across 4+ articles for three
weeks after it passed, caught only by a manual gap review. Tense is
semantics, but past-date-near-future-marker is a string/date
comparison. `check-dates` flags a past date co-occurring on a line with
a future-tense marker (will / expected / retires / deadline / by then /
…); ISO and month-year forms (month-year resolves to month END — "end
Aug 2026" isn't stale until September); frontmatter `updated:`, code,
provenance-tag dates, and dated log headings are masked (all
historical by nature). `--today` time-travels for previews — the field
corpus's next known bomb ("ICD 4.2 expected ~end Aug 2026") flags under
`--today 2026-09-15` and is silent today, fixtured exactly so.

Placement decision worth recording: warn-only, sweep + non-blocking CI,
NEVER the commit gate — findings appear because *time passed*, not
because of the commit at hand, and a gate that fails on unrelated
commits teaches people to bypass it. Different failure physics from
every other check in the suite.
