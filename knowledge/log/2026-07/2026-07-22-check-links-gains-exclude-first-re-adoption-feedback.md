## [2026-07-22] tooling | check-links gains --exclude (first re-adoption feedback)

Adopting the suite back into the originating field repo, `check-links`
surfaced 49 problems — most genuinely broken (archived files whose links
were never updated, wrong relative paths, ambiguous `[[name]]` wikilinks
across areas), but a class of hits landed in **append-only log archives**,
whose entries are frozen narrative and must not be retro-edited for link
hygiene. Added a repeatable `--exclude <glob>` (relative to the knowledge
dir) so those surfaces are skipped while still counting as link
*targets*. Field lesson worth keeping: the first run of a new mechanical
check on a mature repo is an audit, not a gate — triage before wiring it
into hooks.
