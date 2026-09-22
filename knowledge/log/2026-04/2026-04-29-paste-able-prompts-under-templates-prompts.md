## [2026-04-29] new surface | paste-able prompts under templates/prompts/

Two prompt files shipped under `templates/prompts/`:
`first-articles-brownfield.md` and `first-articles-greenfield.md`.
Each is a self-contained instruction block an adopter pastes into
Claude after running install (or any time they want to seed their
first three articles). The prompts encode the methodology
constraints — schema reference, same-task rule, "thin is fine,"
no speculative `affects:`, no back-fill past three — so a fresh
Claude session with no project context produces methodology-
compliant articles instead of generic "let me document this codebase
for you" output.

Decision: **prompts ship as markdown files in the repo, not as
shell-string-literals inside a future install.sh.** Reasons in
`concepts/methodology/prompts.md` (new): they're load-bearing
methodology surface, they version with reviewable diffs, schema
changes affect them, and they're discoverable for adopters who
return later.

Greenfield vs. brownfield split:
- Brownfield prompt scans the codebase: hot-spot modules, decision-
  dense areas, onboarding pain points. Caps at 3, no back-fill.
- Greenfield prompt asks 3–5 anchor questions first, then writes
  three "north star" articles with empty `affects:` (filled when
  the matching code lands).

Same-task collateral:
- New article `concepts/methodology/prompts.md` covers `templates/
  prompts/**`. Captures the load-bearing argument and the "what
  makes a good prompt" criteria (self-contained, constraint-stating,
  one screen, output-shaped).
- README "What's in this repo" gains a row for `templates/prompts/`.
- `templates/prompts/README.md` is the adopter-facing index for the
  directory.
- `index.md` adds the prompts article row.

The install.sh design (in conversation; not yet written) will copy
the appropriate prompt file based on greenfield/brownfield
detection and reference it in the post-install summary so adopters
can paste it into Claude as the first post-install action.
