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

## Bypass behaviour

All hook frameworks let contributors bypass with
`git commit --no-verify`. That's by design — sometimes you want to
commit a half-broken state and fix it next. The PR-time GitHub
Action is the safety net that catches `--no-verify` drift before
merge.
