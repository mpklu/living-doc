# Living Docs — Drift Check Action

A GitHub Action that enforces the same-task rule at PR-review time. It reads the article-mapping table from your project's `CLAUDE.md` and verifies that any PR touching mapped code paths also touches the corresponding articles. If a PR violates the rule, the action posts a comment on the PR and fails the check.

## Why this exists

The agent enforces the same-task rule at **write-time** (when generating code, it also updates the matching article). This action enforces it at **review-time** (rejecting PRs that slipped through without article updates). Together they make the rule extremely hard to silently violate.

The action complements but does not replace the agent's discipline — it's a safety net for the human-driven cases (manual edits, PRs from contributors who don't use Claude, hotfixes pushed under pressure).

## What it checks

Reads `CLAUDE.md` and looks for a table with this header:

```markdown
| When you change... | Update this article |
| --- | --- |
| `src/some/path.py` | `concepts/x.md` |
| The classification workflow | `concepts/classification-workflow.md` |
```

The first column can be:

- A **glob-like path** (`src/*.py`, `workflows/voicemail.py`) — matched via `fnmatch`.
- A **natural-language description** ("The classification workflow") — matched by keyword against changed file paths.

The second column must contain a backticked path to a `.md` file (relative to the repo root, or to the `knowledge/` directory).

For each PR, the action:

1. Diffs the PR's changes against the base branch.
2. For each row in the mapping table, checks whether any changed file matches the code pattern.
3. If yes, checks whether the corresponding article was also changed in the PR.
4. If not, records a violation.
5. Posts a single PR comment summarizing all violations and fails the check (or just warns, configurable).

## Usage

Add this to your repo as `.github/workflows/living-docs-drift.yml`:

```yaml
name: Living Docs Drift Check
on:
  pull_request:
    types: [opened, synchronize, reopened]
permissions:
  contents: read
  pull-requests: write
jobs:
  drift-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: mpklu/living-doc/actions/drift-check@main
```

See `example-usage.yml` in this directory for a fully-configured example.

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `claude-md-path` | `CLAUDE.md` | Path to the file containing the article-mapping table. |
| `knowledge-dir` | `knowledge` | Path to the knowledge directory. Article paths in the mapping table are resolved relative to this. |
| `base-ref` | _(auto)_ | Base ref to diff against. Defaults to the PR base branch. |
| `fail-on-violation` | `true` | Fail the check on violations. Set to `false` to only warn. |
| `comment-on-pr` | `true` | Post a comment on the PR when violations are detected. |

## Outputs

| Output | Description |
| --- | --- |
| `violations` | Number of violations detected (`0` if none). |
| `report` | Markdown-formatted report of the check results. |

## Limitations and caveats

- **Glob patterns are simple.** The action uses `fnmatch`, which doesn't support `**` for recursive matching. If your mapping table uses recursive patterns, broaden them (e.g., `src/x/*.py` rather than `src/x/**/*.py`) or rewrite as multiple rows.
- **Natural-language patterns are approximate.** When a mapping row uses prose ("The customer-lookup agent"), the action does keyword matching against changed file paths. False positives and negatives are possible. For sensitive rules, prefer explicit path patterns.
- **The action doesn't validate article quality.** It only checks that *some* change was made to the article in the same PR. The agent's write-time discipline is still responsible for the article being correct.
- **No table = no check.** If `CLAUDE.md` doesn't have the recognized table format, the action emits an informational note and passes. This is intentional — early-stage brownfield retrofits often have empty tables.

## Local testing

You can run the script locally before configuring the action:

```bash
cd /path/to/your/repo
GITHUB_BASE_REF=main \
CLAUDE_MD_PATH=CLAUDE.md \
KNOWLEDGE_DIR=knowledge \
FAIL_ON_VIOLATION=false \
python3 /path/to/living-doc/actions/drift-check/drift_check.py
```

The script reports violations to stdout and exits 0 when `FAIL_ON_VIOLATION=false`.
