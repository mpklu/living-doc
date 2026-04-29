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

## Concepts

### `methodology/` — decisions about the methodology itself

| Article | Covers | Updated |
| --- | --- | --- |
| [dogfooding](concepts/methodology/dogfooding.md) | Why this repo applies its own methodology; what's different about a meta-repo | 2026-04-29 |
| [frontmatter-as-source-of-truth](concepts/methodology/frontmatter-as-source-of-truth.md) | Article metadata schema; canonical home for `affects`, `status`, `load_bearing` | 2026-04-29 |
| [affects-globs](concepts/methodology/affects-globs.md) | Code↔article mapping via `affects:` frontmatter; auto-generated table | 2026-04-29 |
| [local-vs-pr-enforcement](concepts/methodology/local-vs-pr-enforcement.md) | Layered defense: local pre-commit + PR Action; same logic, two firing points | 2026-04-29 |
| [procedural-vs-principle](concepts/methodology/procedural-vs-principle.md) | Same-task rule expressed as a checklist + red-flag phrases, not just principle | 2026-04-29 |

### `tooling/` — internals

_(empty — populate when `drift-check`, the Skill, or the templates are next modified)_

## Connections

_(empty — populate when an article spans methodology + tooling)_
