# {{Project Name}}

{{One-paragraph project description. What does this project do? Who uses it?
Why does it exist? Replace this paragraph with your own.}}

## Methodology

This project follows the living-documentation methodology described at
https://github.com/mpklu/living-doc.
The first principle ("capture first, refine second") and the same-task
rule from that repository's `LIVING_DOCS_OVERVIEW.md` apply here.

## Source of Truth

The knowledge base in `knowledge/` is the source of truth for this project.
It must always mirror the code. Entry point: `knowledge/index.md`.
Compile log: `knowledge/log.md`.

### The rule

Every code change that alters behaviour, config, models, or architecture
must update the relevant `knowledge/concepts/*.md` article(s) in the same
task and append an entry to `knowledge/log.md`. Don't batch knowledge
updates for later.

**Capture first, refine second:** when in doubt about whether a change is
documentation-relevant, write the update anyway. When in doubt about where
a new article belongs, pick the closest fit and write it. The user reviews
and refines. Missing context is unrecoverable; an imperfect article costs
minutes.

### What lives where

| Location | Contains | Authority |
| --- | --- | --- |
| `knowledge/concepts/` | Standalone reference articles, grouped by area | How each thing works and why |
| `knowledge/connections/` | Cross-concept articles | How the pieces fit together |
| `src/{{your-package}}/` | Implementation | What the system does |
| `tests/` | Tests with sanitized fixtures | Testable behaviour |
| `.env` | Real credentials (gitignored) | Local config |

### Article mapping — update these when the matching code changes

This table is populated from day one of greenfield. As you add new modules
or external integrations, add new rows here.

| When you change... | Update this article |
| --- | --- |
| Folder structure or layer boundaries | `concepts/{{project}}/platform-architecture.md` |
| A data model (field added/removed/required-flipped) | `concepts/{{project}}/data-models.md` |
| The main workflow logic | `concepts/{{project}}/{{workflow-name}}-workflow.md` |
| The LLM agent or its tools (if applicable) | `concepts/{{project}}/{{agent-name}}-agent.md` |
| Webhook or API handling for {{external-system}} | `concepts/{{external-system}}/{{system}}-integration.md` |
| Env vars, per-environment config | `concepts/{{project}}/configuration.md` |
| Local dev setup, sandbox, replay tools | `concepts/{{project}}/local-development.md` |
| Test conventions, fakes, fixtures | `concepts/{{project}}/testing-strategy.md` |

### When the agent encounters code without a matching article

Write the first thin article in the same task. Place as:

- `concepts/{{project}}/{topic-kebab-case}.md` for an internal concept.
- `concepts/{external-system}/{topic}.md` for an external integration. Create
  a new area subdirectory if the system isn't already covered.
- `connections/{topic}.md` for a cross-cutting article describing how
  multiple existing concepts interact.

Capture the **why** — context, constraints, alternatives ruled out — not
just the post-change state of the code. Add a row to the article-mapping
table above. Note the addition in `log.md`.

### How to catch drift

After finishing implementation, ask: "does anything in `knowledge/` now
contradict what I just built?" Check signatures, field lists, config
tables, folder structure, and env var names. **Real data beats the article**
— if a field the article says is required turns out to be absent in real
payloads, update the article to match reality, not the other way around.
Add a compile entry to `knowledge/log.md` listing the articles touched.

## Project Structure

```
{{outline of src/, tests/, config/, etc.}}
```

## Key Commands

```bash
{{your-package-manager}} install
{{your-test-runner}}
```
