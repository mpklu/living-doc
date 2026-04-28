# PR template snippet

Add the snippet below to your project's `.github/pull_request_template.md` (or equivalent for your forge). It makes the same-task rule visible at review time so reviewers can hold the line.

---

## Pre-merge checks

- [ ] Tests pass
- [ ] Linter passes
- [ ] **Knowledge updated** — does this change affect anything covered by an article in `knowledge/`?
  - If yes: the matching article and `knowledge/log.md` are updated in this PR.
  - If the affected area is not yet covered by an article: a first thin article has been written in this PR (see `CLAUDE.md`'s article-mapping table for placement guidance).
  - If unsure: a short note in `knowledge/log.md` describing the change is sufficient — when in doubt, default to writing.
