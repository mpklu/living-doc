# Living Documentation Methodology

> _A documentation pattern for AI-assisted codebases._
> _Every code change updates the matching article in the same task. The agent enforces the rule._

This repository defines a methodology for keeping software documentation as durable as the code it describes. It exists because the cost of writing and maintaining documentation has collapsed — AI agents in the development loop can produce and update articles in the same change that produces the code, removing the historical reason teams gave up on documentation under deadline pressure.

The methodology is small (three documents you can read in 30 minutes) and disciplined (one rule, enforced by the AI agent reading `CLAUDE.md` on every interaction). It works for both new projects and existing ones, single repos and multi-repo workspaces. For more about this approach, see [this blog post](https://mpklu.github.io/posts/living-knowledge-base/)



## How to use this repo

Use this one liner in Claude Code:

```
Apply living-doc: https://github.com/mpklu/living-doc/tree/main/skills/living-docs
```

For details see [Full README](./README_OLD.md)

