# LIVING_DOC knowledge base

Articles documenting the methodology's *own* decisions and tooling
internals. The published methodology (overview + adoption guides) is the
adopter-facing surface; articles here capture the *why* — alternatives
considered, constraints, decisions made when, what failed and was
replaced.

**Retrofit start:** 2026-04-29. Coverage is intentionally partial. New
methodology refinements and tooling changes get articles in the same task
that produces them. Existing prose stays put until the next time it's
touched.

The article tables below are **generated** from each article's
frontmatter (`description:` fills "Covers") by `scripts/build-index` —
edit the frontmatter, not the tables. CI-checkable with
`build-index --check`.

## Concepts

### `methodology/` — decisions about the methodology itself

<!-- build-index:begin dir=concepts/methodology -->
| Article | Covers | Updated |
| --- | --- | --- |
| [affects-globs](concepts/methodology/affects-globs.md) | Code↔article mapping via `affects:` frontmatter; auto-generated table | 2026-07-22 |
| [claim-provenance](concepts/methodology/claim-provenance.md) | Inline provenance tags — *(code: path:line)* · *(bench: date)* · *(field: incident)* · *(reported: who)* · *(inferred)* — so readers (human or agent) can calibrate trust per claim, not per article. The fix for AI-written docs' worst failure mode: confident-sounding inference read as fact later | 2026-07-22 |
| [dogfooding](concepts/methodology/dogfooding.md) | Why this repo applies its own methodology; what's different about a meta-repo | 2026-04-29 |
| [facts-register](concepts/methodology/facts-register.md) | Optional per-article `## Facts` section (atomic, provenance-tagged lookup facts) concatenated per area into generated knowledge/facts/<area>.md files — so a needle query loads one ~3KB surface instead of 20–60KB of prose. Read-path economics: writing is cheap now; context tokens at read time are the scarce resource | 2026-07-22 |
| [frontmatter-as-source-of-truth](concepts/methodology/frontmatter-as-source-of-truth.md) | Article metadata schema; canonical home for `affects`, `status`, `load_bearing` | 2026-04-29 |
| [local-vs-pr-enforcement](concepts/methodology/local-vs-pr-enforcement.md) | Layered defense: local pre-commit + PR Action; same logic, two firing points | 2026-07-22 |
| [procedural-vs-principle](concepts/methodology/procedural-vs-principle.md) | Same-task rule expressed as a checklist + red-flag phrases, not just principle | 2026-04-29 |
| [prompts](concepts/methodology/prompts.md) | Why we ship paste-able Claude prompts under `templates/prompts/`; what makes a good one; drift risk via the schema | 2026-04-29 |
| [scripts-over-reasoning](concepts/methodology/scripts-over-reasoning.md) | Anything checkable by string/date/path comparison must be a script; AI reasoning is reserved for semantics. The boundary rule that keeps agent effort on judgment instead of bookkeeping | 2026-07-22 |
| [session-handoff](concepts/methodology/session-handoff.md) | Bridging context boundaries; planned `skills/session-handoff/` skill that captures cursor + open items at session-end | 2026-04-29 |
| [what-cache-why-asset](concepts/methodology/what-cache-why-asset.md) | Budget article prose by derivability: what-sections are caches of the code (falling value, recurring invalidation bill — keep them thin, pointed, tagged); why-sections are the only record of the non-derivable (rejected alternatives, constraints, negative results, field incidents — zero maintenance, appreciating). The derivability test decides which is which | 2026-07-22 |
<!-- build-index:end -->

### `tooling/` — internals

<!-- build-index:begin dir=concepts/tooling -->
| Article | Covers | Updated |
| --- | --- | --- |
| [drift-check](concepts/tooling/drift-check.md) | `drift_check.py` internals: dual mapping sources, hand-rolled frontmatter parser, `**` glob matcher, free-text fallback | 2026-07-22 |
| [install-script](concepts/tooling/install-script.md) | `install/install.sh` internals: bash 3.2+, manifest-driven, atomic per-file write, idempotent re-run, detection bias toward brownfield | 2026-04-29 |
| [maintenance-tools](concepts/tooling/maintenance-tools.md) | The local maintenance suite: link checking, index generation from frontmatter, updated:-date bumping, drift-sweep worklists, and log rotation — five stdlib-only tools sharing the validate_articles frontmatter parser | 2026-07-22 |
| [validate-articles](concepts/tooling/validate-articles.md) | Frontmatter schema validator: hand-rolled YAML parser, cross-reference check, schema-as-contract caveat | 2026-07-22 |
<!-- build-index:end -->

## Connections

_(empty — populate when an article spans methodology + tooling)_
