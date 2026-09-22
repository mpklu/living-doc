## [2026-07-22] tooling | check-affects linter + drift-check keyword fallback fenced to legacy tables

The commit gate's maiden run in the field caught four latent `affects:`
bugs by trial-and-error (two blocked commits); this turns that class
into a pre-commit linter. `check-affects`: free text inside `affects:`
and globs claiming `knowledge/**` trees are ERRORS; dead globs and dead
bare literals WARN (liveness judged against the repo plus repeatable
`--source-root`, so cross-repo globs aren't false-flagged); a live
root-level literal like `CLAUDE.md` stays silent. `external:`-prefixed
entries — the field adoption's cross-repo convention — are now blessed
upstream: exempt in the linter and skipped by drift-check's mapping.

drift-check itself is fixed, not just linted around: `MappingRow` gains
`source`, and affects-sourced rows match with `force_glob` — the
natural-language keyword fallback (which turned the token "data" into a
match on "datadog") is now unreachable except for legacy CLAUDE.md
table rows, its original purpose. Regression-fixtured: a keyword-bait
file no longer matches a free-text affects entry; real globs still
flag. Hygiene rules written into affects-globs.md; drift-check.md
updated. The linter's first self-run on this repo found one aspirational
dead glob (session-handoff's planned `skills/session-handoff/**`) —
warning-level and informative, left standing until the skill exists.
