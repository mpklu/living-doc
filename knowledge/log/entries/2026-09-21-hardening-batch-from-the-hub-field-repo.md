## 2026-09-21 — Hardening batch from the hub field repo: index, log, two readers, decisions, hub, tests

- **Source.** One day of tooling work in the ~130-article production hub (knowledger-trans), ported here
  as tools + tests + seven methodology articles + a hub adoption guide; this repo's own `knowledge/`
  migrated in the same commit (28 log entries split into files; 4 generated `_index.md`; `scopes.md`).
- **Breaking for adopters:** `index.md` → generated `_index.md` per directory + curated `scopes.md`;
  `log.md` → `log/entries/` files. Templates, both guides, glossary, overview, prompts, skill and the
  install manifest updated; workspace-level template too.
- **Kept upstream-strict:** `validate_articles.py` keeps this repo's required fields and status enum (the
  field repo relaxed them locally); only the skip lists changed.
- **Articles:** new `hub-knowledge-base`, `two-readers-one-article`, `index-is-a-cache`,
  `decisions-in-the-article`, `log-as-files`, `sweep-by-repo-head`, `token-budget-per-surface`; extended
  `facts-register`, `claim-provenance`, `dogfooding`, `tooling/maintenance-tools`.
- **Suggested tag:** 1.0.0 — the knowledge/ shape changed.
