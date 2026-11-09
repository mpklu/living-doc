<!-- build-index:generated — edit article frontmatter (rows) or scopes.md (scope lines), not this file -->

# concepts/methodology

Decisions about the methodology itself: what the rules are, why, what was tried and dropped.

| Article | Title | Status | Updated | F | D | Affects |
| --- | --- | --- | --- | --- | --- | --- |
| concepts/methodology/affects-globs.md | affects globs — code↔article mapping | thin | 2026-07-22 |  |  | article-frontmatter.schema.json |
| concepts/methodology/claim-provenance.md | Claim provenance — grade claims by how they were verified | thin | 2026-09-21 |  |  |  |
| concepts/methodology/decisions-in-the-article.md | Decisions live in the article; the story lives in the log | thin | 2026-11-09 |  |  | build_index.py |
| concepts/methodology/dogfooding.md | Dogfooding the methodology | thin | 2026-09-21 |  |  | CLAUDE.md, README.md |
| concepts/methodology/facts-register.md | Facts register — the read-path layer between index and prose | thin | 2026-09-21 | F |  |  |
| concepts/methodology/frontmatter-as-source-of-truth.md | Frontmatter as source of truth | thin | 2026-09-21 |  |  | article-frontmatter.schema.json, knowledge |
| concepts/methodology/handbook-layer.md | The handbook — a current-state layer for every reader, kept fresh by its sources | thin | 2026-11-09 |  | D1 | check_handbook.py, check-handbook, +1 |
| concepts/methodology/hub-knowledge-base.md | Hub knowledge base — one KB for many repos it does not contain | thin | 2026-09-21 |  |  | bootstrap.py, kb_paths.py, +2 |
| concepts/methodology/index-is-a-cache.md | The index is a cache — generate it per directory, curate only scope lines | thin | 2026-11-09 |  |  | build_index.py |
| concepts/methodology/local-vs-pr-enforcement.md | Local + PR-time enforcement — layered defense | thin | 2026-07-22 |  |  |  |
| concepts/methodology/log-as-files.md | The log is files — one entry per file, never rendered, rolled by renaming | thin | 2026-09-21 |  |  | roll_log.py |
| concepts/methodology/procedural-vs-principle.md | Procedural compliance — checklist, not principle | thin | 2026-09-21 |  |  | CLAUDE.md |
| concepts/methodology/prompts.md | Paste-able prompts as methodology surface | thin | 2026-09-21 |  |  | prompts |
| concepts/methodology/scripts-over-reasoning.md | Scripts over reasoning — mechanize the checkable | thin | 2026-07-22 |  |  |  |
| concepts/methodology/session-handoff.md | Session handoff — bridging context boundaries | thin | 2026-04-29 |  |  | session-handoff |
| concepts/methodology/sweep-by-repo-head.md | Sweep by repo HEAD before reading prose | thin | 2026-09-21 |  |  | sweep_report.py |
| concepts/methodology/token-budget-per-surface.md | A token budget per surface — what is read when, and how big it may be | thin | 2026-11-09 |  |  | kb_status.py |
| concepts/methodology/two-readers-one-article.md | Two readers, one article — facts for agents, plain terms for people | thin | 2026-09-21 |  |  | build_facts.py |
| concepts/methodology/what-cache-why-asset.md | The what is a cache; the why is a primary source | thin | 2026-07-22 | F |  |  |
