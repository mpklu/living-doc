# Paste-able prompts

These are curated prompts you paste into Claude (Claude Code, claude.ai, or any Claude-powered tool) at moments where the methodology calls for a workflow that's awkward as prose but trivial as a prompt.

Each prompt is self-contained — a fresh Claude session with no project context can run it after reading `LIVING_DOCS_OVERVIEW.md` and `CLAUDE.md`.

## Available prompts

| File | Use when |
| --- | --- |
| [`first-articles-brownfield.md`](first-articles-brownfield.md) | You've just adopted living-docs on an existing codebase and need to seed the first three articles. Claude scans the repo, picks three seams (hot-spots / decision-dense areas / onboarding pain points), and writes thin articles. |
| [`first-articles-greenfield.md`](first-articles-greenfield.md) | You've just adopted living-docs on a new project. Claude asks 3–5 anchor questions about intent, then writes three "north star" articles capturing planned shape. |

## How to use

1. Open Claude Code (or claude.ai) in your project's root directory.
2. Open the prompt file for your situation.
3. Copy the section below the `---` separator (the part above is for you, not Claude).
4. Paste into Claude. Answer any questions Claude asks.
5. Review the generated articles before committing.

## Why ship these

See `knowledge/concepts/methodology/prompts.md` (in the upstream LIVING_DOC repo, or your own copy if you've adopted) for the methodology rationale. Short version: prompts are load-bearing — without them, adopters reach the "write your first articles" step and stall, or write articles that violate constraints they didn't know existed.

## Contributing

Prompts evolve. If you find a phrasing that produces better articles, open a PR. Keep prompts to ~80 lines and one workflow each.
