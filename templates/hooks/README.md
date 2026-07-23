# Pre-commit hook templates

Drop one of these into your project to run the drift check at commit
time, not just at PR time. See
`knowledge/concepts/methodology/local-vs-pr-enforcement.md` for why
both layers matter.

All three templates assume `scripts/drift-check` is present in the
repo (copy from the LIVING_DOC repo's `scripts/drift-check`, or symlink
into a vendored location).

## Option 1: pre-commit framework

For projects using [pre-commit](https://pre-commit.com).

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: living-docs-drift-check
        name: Living Docs drift check
        entry: scripts/drift-check
        language: system
        pass_filenames: false
        always_run: true
        # HEAD = staged-only diff (the about-to-be-committed set).
        # See "Choosing a --base-ref" below.
        args: [--base-ref, HEAD]
```

Install once: `pre-commit install`. Subsequent commits run the check.

## Option 2: husky

For Node.js projects using [husky](https://typicode.github.io/husky).

`.husky/pre-commit`:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

scripts/drift-check --base-ref HEAD || exit 1
```

`chmod +x .husky/pre-commit` after creation.

## Option 3: lefthook

For projects using [lefthook](https://github.com/evilmartians/lefthook).

`lefthook.yml`:

```yaml
pre-commit:
  commands:
    drift-check:
      run: scripts/drift-check --base-ref HEAD
```

Install once: `lefthook install`.

## Choosing a `--base-ref`

The drift check needs to know "what's changing in this commit?" so it
can match changed files against article `affects:` globs. Three
options:

- **`HEAD`** — staged-only diff (`git diff --cached`): the exact set
  the about-to-be-created commit will contain. Recommended for
  pre-commit. Unstaged working-tree edits in unrelated files are
  intentionally excluded — including them would flag articles whose
  `affects:` happens to match dirty paths the contributor isn't
  actually committing.
- **`HEAD~1`** — diff the just-finished commit against its parent.
  Useful for post-commit verification or in `pre-push` hooks.
- **`origin/main`** — diff the entire branch. Useful in CI mirroring
  the PR-time check.

For pre-commit, **`HEAD`** is the right default and what all three
hook templates above pass.

## Companion hooks: bump-updated and check-links

Two more local checks pair well with the drift check (both live in
`scripts/`, same copy/symlink approach; see
`knowledge/concepts/tooling/maintenance-tools.md`):

- **`scripts/bump-updated --staged --check`** — fails the commit if a
  staged knowledge article's `updated:` isn't today. Fix is one command
  (`scripts/bump-updated --staged`, then re-stage). Checking rather than
  auto-mutating keeps the hook side-effect-free.
- **`scripts/check-links`** — fails the commit if any `[[wikilink]]` or
  relative link in `knowledge/` is broken or ambiguous (catches renames
  and deletions the moment they happen, not when a reader hits them).
- **`scripts/build-index --check`** — fails if generated index tables are
  stale (fix: `scripts/build-index`, re-stage).
- **`scripts/build-facts --check`** — fails if generated `knowledge/facts/`
  surfaces are stale or orphaned (fix: `scripts/build-facts`, re-stage).

pre-commit framework example (append to the hooks list):

```yaml
      - id: living-docs-bump-updated
        name: Living Docs updated: check
        entry: scripts/bump-updated
        language: system
        pass_filenames: false
        always_run: true
        args: [--staged, --check]
      - id: living-docs-check-links
        name: Living Docs link check
        entry: scripts/check-links
        language: system
        pass_filenames: false
        always_run: true
      - id: living-docs-build-index
        name: Living Docs index freshness
        entry: scripts/build-index
        language: system
        pass_filenames: false
        always_run: true
        args: [--check]
      - id: living-docs-build-facts
        name: Living Docs facts freshness
        entry: scripts/build-facts
        language: system
        pass_filenames: false
        always_run: true
        args: [--check]
```

(husky/lefthook: add the same commands as extra lines/commands.)

**No hook framework?** A single versioned gate script that runs all the
checks, exec'd from a plain `.git/hooks/pre-commit`, works everywhere with
zero dependencies — the field adoption ships one as `scripts/pre-commit-gate`
(with an `--install` mode that writes the two-line git hook). Pair it with
the same commands in CI: hooks are bypassable by `--no-verify`, CI is the
safety net.

## Cross-repo: the `Knowledge:` trailer hook (product repos)

Drift-check guards the knowledge repo; the same-task rule's other half
lives in the PRODUCT repos, where code changes must name the article they
obligate. `check-trailer` enforces the trailer convention as a
`commit-msg` hook **installed in each product repo**:

```bash
cd /path/to/ProductRepo
/path/to/knowledge-repo/scripts/check-trailer --install --knowledge-repo /path/to/knowledge-repo
```

A commit whose staged paths match any article's `affects:` globs (or an
`external:` entry naming this repo) is blocked unless the message carries
`Knowledge: <article>` or an explicit `no knowledge impact: <reason>`.
The block prints the mapped article list and a paste-ready trailer.
Start with `--warn-only` in the hook line for a soft rollout. Note the
trade-off honestly: product repos usually have no CI net behind
`git commit --no-verify` — this hook is the enforcement, so keep it
helpful enough that nobody wants to bypass it.

## Bypass behaviour

All hook frameworks let contributors bypass with
`git commit --no-verify`. That's by design — sometimes you want to
commit a half-broken state and fix it next. The PR-time GitHub
Action is the safety net that catches `--no-verify` drift before
merge.
