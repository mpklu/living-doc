## [2026-07-22] tooling | validate-articles skips log/ + facts/ dirs

Caught right after the facts-register commit: the generated
`knowledge/facts/*.md` files (sentinel, no frontmatter) failed
frontmatter validation — validate-articles skipped only `index.md` /
`log.md` by name, not the `log/` archive dir or the new generated
`facts/` dir. Skipped both by directory, matching sweep-report's rule.
Lesson repeated from the adoption audit: every new generated surface
must be walked through ALL existing checkers, not just the new one.
