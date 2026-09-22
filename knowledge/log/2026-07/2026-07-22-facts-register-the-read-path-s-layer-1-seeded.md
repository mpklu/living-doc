## [2026-07-22] methodology | facts register — the read path's layer 1 (seeded)

Third pattern from the field review, completing the progressive-disclosure
ladder: `description:`/index answer *where do I look?* (layer 0), the new
**facts register** answers *what is the value?* (layer 1), prose keeps
*why* (layer 2), the log keeps *when/how learned* (layer 3). Motivation is
read-path economics: with AI in the loop, writing is cheap — **context
tokens at read time are the scarce resource**, and the field repo's most
common agent reads were needle queries (a port, a folder, an error code)
paying 20–60KB prose loads for one-line answers.

Mechanism: an article MAY carry a `## Facts` section — 8–15 atomic,
claim-provenance-tagged bullets — and `build-facts` concatenates them per
`area:` into generated `knowledge/facts/<area>.md` (sentinel first line,
orphan cleanup, `--check` gate). Articles stay the single source; facts
sections are *extracted, never invented* (a fact with no home in the
prose means write the prose claim first). Rules in
`concepts/methodology/facts-register.md` (itself carrying a Facts
section, as does `tooling/maintenance-tools.md` — first dogfood).
`sweep-report` now skips `log/` archives and generated `facts/` (the
noise nit noted at adoption). Adopter surface: glossary entry; ROADMAP
candidate marked seeded; guides/templates fold-in deferred until
field-validated, per house convention.
