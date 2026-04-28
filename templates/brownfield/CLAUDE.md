# {{Project Name}}

{{One-paragraph project description.}}

## Methodology

This project is adopting the living-documentation methodology described at
https://github.com/mpklu/living-doc

The first principle ("capture first, refine second") and the same-task
rule apply here. This is a **brownfield retrofit** — see
`BROWNFIELD_ADOPTION_GUIDE.md` in the methodology repo for the
"document on touch" mindset and how the article-mapping table grows
gradually rather than being populated speculatively.

## Source of Truth

The knowledge base in `knowledge/` is becoming the source of truth for this
project. As of the retrofit start (see `knowledge/log.md`), it covers a
subset of the codebase. Code paths without articles are documented on touch
— the next time someone changes them, that's when the first thin article
gets written.

Entry point: `knowledge/index.md`. Compile log: `knowledge/log.md`.

### The rule

Every code change that alters behaviour, config, models, or architecture
must update the relevant `knowledge/concepts/*.md` article(s) in the same
task and append an entry to `knowledge/log.md`. If the affected code path
does **not yet** have an article, write the first thin article in the same
task — don't defer.

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
| {{existing-wiki-or-docs-location}} | Legacy docs | Reference; superseded by `knowledge/` as articles are added |

### Article mapping — populated gradually

In a brownfield retrofit, this table starts empty and grows as articles are
written for code paths that get touched. Add a row each time you create a
new article.

| When you change... | Update this article |
| --- | --- |
| _(first row goes here when the first article is written)_ | |

### When the agent encounters code without a matching article

This is the most common case during the first 2–3 months of retrofit.
Write the first thin article in the same task. Place as:

- `concepts/{{project}}/{topic-kebab-case}.md` for an internal concept.
- `concepts/{external-system}/{topic}.md` for an external integration. Create
  a new area subdirectory if the system isn't already covered.
- `connections/{topic}.md` for a cross-cutting article describing how
  multiple existing concepts interact.

Capture the **why** — context, constraints, alternatives ruled out — not
just the post-change state of the code. Add a row to the article-mapping
table above. Note the addition in `log.md`.

**Document on touch, not on inventory.** Don't write articles for code paths
you're not touching. Don't run a documentation sprint. Articles are written
reactively, in the same task as the code change that motivated them.

### Legacy documentation

If existing wiki / README / design docs exist, they remain as reference
material but are no longer the source of truth. As code paths are touched
and articles are written, fold relevant legacy doc content into the new
article. Mark the legacy doc as "superseded by `knowledge/concepts/X.md`".
Don't migrate proactively.

### How to catch drift

After finishing implementation, ask: "does anything in `knowledge/` now
contradict what I just built?" Check signatures, field lists, config
tables, folder structure, and env var names. **Real data beats the article**
— if a field the article says is required turns out to be absent in real
payloads, update the article to match reality, not the other way around.
Add a compile entry to `knowledge/log.md` listing the articles touched.

Schedule a periodic drift sweep (once a sprint or once a month, ~30
minutes): scan articles by oldest `updated:` date first, fix any drift,
log the sweep.

## Project Structure

```
{{outline of src/, tests/, config/, etc. — describe the existing structure}}
```

## Key Commands

```bash
{{your-package-manager}} install
{{your-test-runner}}
```
