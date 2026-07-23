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

## what-cache-why-asset — [../concepts/methodology/what-cache-why-asset.md](../concepts/methodology/what-cache-why-asset.md)

- **The derivability test**: *re-derivable by a competent agent with the checkouts in minutes?* → cache (thin) · *needs a bench run, vendor call, production incident, or time machine?* → asset (rich prose)
- **What depreciates for two reasons**: re-derivation cost keeps falling AND every what-sentence carries a recurring invalidation bill (drift checks, sweeps, `updated:` hygiene)
- **Why has zero maintenance cost**: a historical fact can't drift — only be superseded, and the supersession is itself informative
- **Non-derivable content**: rejected alternatives · external constraints · negative results · field incidents and their symptom→cause mappings
- **Sanctioned cache form**: `## Facts` blocks ([[facts-register]]) + `*(code: path:line)*` pointers ([[claim-provenance]]) — atomic, tagged, staleness-gated
- **Exception**: operator-facing docs stay what-heavy (their readers don't grep source)
