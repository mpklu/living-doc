# Roadmap

Planned phases for the living-documentation methodology after the initial publication of this repo. The methodology itself (the three core docs) is stable; the phases below are about making it more practical to adopt and harder to silently violate.

Each phase is sized to deliver standalone value — finishing Phase 1 doesn't require committing to Phase 3.

---

## Phase 0 — Initial publication (current)

**Status:** in progress / shipping shortly.

**Deliverables:**

- ✅ Three core methodology documents (`LIVING_DOCS_OVERVIEW.md`, `GREENFIELD_ADOPTION_GUIDE.md`, `BROWNFIELD_ADOPTION_GUIDE.md`)
- ✅ `GLOSSARY.md` — vocabulary reference
- ✅ `README.md` — repo landing page with three usage patterns
- ✅ `LICENSE` — CC-BY-4.0
- ✅ `CHANGELOG.md` — initial entry
- ✅ `templates/greenfield/` — copy-paste starter for new projects
- ✅ `templates/brownfield/` — copy-paste starter for existing projects
- ✅ `templates/workspace-level/` — copy-paste starter for multi-repo workspaces
- ✅ `templates/pr-template-snippet.md` — PR-template fragment for the same-task checkbox
- ✅ `skills/living-docs/` — Claude Code Skill scaffolding for adopt / audit / sweep
- ✅ `actions/drift-check/` — GitHub Action for PR-time enforcement
- ✅ `ROADMAP.md` (this document)

**Acceptance:** the repo is published on GitHub; README is the landing page; a stranger can read `LIVING_DOCS_OVERVIEW.md` and the appropriate adoption guide in 30 minutes and understand the methodology.

**Estimated effort:** ~1 day to publish (cleanup, repo creation, push). Most artifacts already drafted.

---

## Phase 1 — Validation (weeks 1–2 after publish)

**Goal:** prove the methodology works on a real project, find and fix the first wave of papercuts.

**Deliverables:**

- Apply the methodology to **one of your own active projects** end-to-end. Track how often the agent gets placement right vs. wrong. Track how often the same-task rule gets violated even with the rule in place.
- File issues against this repo for any friction discovered. Each issue becomes a candidate refinement.
- Update the guides in response to friction. Any change is logged in `CHANGELOG.md`.
- **First tagged release: v0.1.0.** Tag once the first round of refinements lands.

**Acceptance:** at least one real project running the methodology successfully; the guides have absorbed at least one round of real-world feedback; v0.1.0 tagged.

**Estimated effort:** ~2–4 hours/week. Mostly observation; refinements are surgical.

---

## Phase 2 — Skill polish and distribution (weeks 3–6)

**Goal:** make the Claude Code Skill the primary adoption interface. Most users should be able to type `/living-docs adopt` and get a working setup without reading the guides.

**Deliverables:**

- Test the Skill against a representative set of project shapes:
  - Greenfield single repo (Python, TypeScript, Go each)
  - Brownfield single repo (small, medium, large)
  - Multi-repo workspace (tightly and loosely coupled variants)
- Refine `SKILL.md` based on what Claude actually does in each scenario. The Skill should produce identical output to copy-pasting the templates and following the guide manually.
- Add `skills/living-docs/INSTALL.md` with clear instructions for both personal (`~/.claude/skills/`) and team-wide (Claude Code plugin) installation.
- Optionally: package as a [Claude Code Plugin](https://docs.claude.com/en/docs/claude-code/plugins) for one-command installation. This requires writing a plugin manifest.
- **Tagged release: v0.2.0.**

**Acceptance:** a developer who has never read the guides can run `/living-docs adopt` and end up with a correctly-configured project. Verified across the three project shapes above.

**Estimated effort:** ~10–15 hours total (testing across project shapes is the long pole).

---

## Phase 3 — PR-time enforcement (weeks 6–10)

**Goal:** the GitHub Action becomes a reliable, low-noise PR check. Teams using it should trust it.

**Deliverables:**

- Battle-test `actions/drift-check/drift_check.py` on real PRs from at least two projects. Tune false-positive and false-negative rates.
- Improve glob support (likely add `**` recursive matching) and refine the natural-language keyword matcher.
- Add a `--dry-run` mode to the script for local testing.
- Consider a **GitLab CI variant** if there's demand.
- Add a **pre-commit hook** version (lower friction than CI; runs on the developer's machine before commit).
- Documentation: `actions/drift-check/TUNING.md` with guidance on writing good mapping table rows that minimize false positives.
- **Tagged release: v0.3.0.**

**Acceptance:** at least one project running the Action on every PR with <5% false-positive rate (over 50+ PRs).

**Estimated effort:** ~15–25 hours, depending on how much tuning the matcher needs.

---

## Phase 4 — IDE / editor surfacing (months 3–4)

**Goal:** bridge the gap between "writing code" and "reading the matching article." Reduces friction for the human side of the same-task rule, especially for code review.

**Deliverables:**

- VS Code extension that, when a code file is open, surfaces:
  - The matching article from the article-mapping table (in a side panel)
  - The article's `updated:` date (highlights stale articles)
  - A button to open the article for editing alongside the code
- Optionally: similar for JetBrains / Cursor / other agent-aware editors.
- **Tagged release: v0.4.0.**

**Acceptance:** one editor extension published to a marketplace, with usage signals.

**Estimated effort:** ~30–50 hours. This is the highest-effort phase; prioritize only if Phases 1–3 reveal that human-side discipline is the bottleneck.

---

## Phase 5+ — Community and evolution (open-ended)

**Goal:** transition from "personal methodology" to "community methodology."

**Possible deliverables:**

- Enable GitHub Discussions on the repo for adopter feedback and edge-case sharing.
- Solicit case studies. Add `case-studies/` directory with 2–3 worked examples from real adopters.
- Versioning policy formalized: SemVer with deprecation policy for breaking changes.
- Translations of the three core docs into other languages, if demand emerges.
- Talks / blog posts / conference submissions (your choice; this isn't a deliverable for the repo, but a separate distribution channel).

---

## Triage criteria — what to drop or defer

This roadmap is ambitious for a single-person project. If time pressure forces choices, drop in this order:

1. **Phase 4 (IDE extension)** — first to drop. Marginal value; high effort.
2. **Phase 3's GitLab variant** — if no demand surfaces.
3. **Phase 2's plugin packaging** — keep manual installation as-is.

**Do not drop:**

- Phase 1 (validation on a real project) — without this, the methodology is theoretical.
- The first tagged release — version pinning is what makes the URL-reference pattern (Pattern 1 in README) work safely.

---

## Risk register

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Methodology requires updates that break adopters | Medium | High | SemVer; major version bumps signal breaking changes; CHANGELOG entries explain migration |
| Skill produces inconsistent output across project shapes | High | Medium | Phase 2's testing matrix; track Skill-vs-manual divergence as a quality signal |
| Drift-check action's natural-language matcher is too noisy in real use | High | Medium | Phase 3's tuning guide; recommend explicit path patterns over prose where possible |
| Methodology turns out to require a stronger team-buy-in mechanism than CLAUDE.md alone | Low | Low | Documented in both adoption guides; nothing actionable until evidence appears |
| Tooling fragments (Claude Code vs. Cursor vs. Codex...) make the agent-instruction layer non-portable | Medium | Medium | Keep `CLAUDE.md` as the canonical filename but document equivalence with `AGENTS.md`, `.cursorrules`, etc. in a future iteration |

---

## How to track progress

When working on a phase:

1. Open a tracking issue per phase ("Phase 2 — Skill polish and distribution").
2. Each deliverable becomes a checkbox in the issue.
3. Refinements to the methodology itself land as PRs that update the relevant guide and append to `CHANGELOG.md`.
4. Tagged releases (`v0.1.0`, `v0.2.0`, ...) close out a phase.

The methodology repo itself follows the methodology: `CHANGELOG.md` is the project log, the three core docs are the source of truth, and any change to behaviour or structure updates them in the same PR. That's the test we hold ourselves to.
