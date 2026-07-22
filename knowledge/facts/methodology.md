<!-- build-facts:generated — edit the articles' ## Facts sections, not this file -->

# Facts — methodology

Atomic lookup facts extracted from the `methodology` articles' `## Facts` sections by `scripts/build-facts`. One small surface for needle queries; open the linked article for the why.

## facts-register — [../concepts/methodology/facts-register.md](../concepts/methodology/facts-register.md)

- **Section marker**: a literal `## Facts` heading; body runs to the next `## ` heading
- **Generated output**: `knowledge/facts/<area>.md`, one per frontmatter `area:` that has ≥1 facts section
- **Sentinel** (first line of generated files): `<!-- build-facts:generated … -->`
- **Commands**: `scripts/build-facts` (write) · `scripts/build-facts --check` (CI gate; also flags orphans) *(code: build_facts.py)*
- **Fact shape**: `- **key**: value *(provenance tag)*` — atomic, one lookup per bullet
- **Single source**: the article's `## Facts` section; generated files are never edited by hand
