"""facts_overlap: a ## Facts bullet that restates a prose sentence scores
high; frontmatter and short bullets are ignored; no Facts → None."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import facts_overlap  # noqa: E402

FM = ('---\nupdated: 2026-01-01\narea: x\n'
      'description: "The generator log lives at /tmp/EclaimGenerator-<uid>.log and MP_ECLAIM_GENERATOR_LOG overrides it"\n---\n')


class FactsOverlapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, body: str) -> Path:
        p = Path(self.tmp.name) / "a.md"
        p.write_text(FM + body, encoding="utf-8")
        return p

    def test_restated_bullet_is_near_verbatim(self) -> None:
        p = self.write("# T\n\nThe generator writes its log file to `/tmp/EclaimGenerator-<uid>.log`; "
                       "set the `MP_ECLAIM_GENERATOR_LOG` environment variable to override that path.\n\n"
                       "## Facts\n\n- Generator log file: `/tmp/EclaimGenerator-<uid>.log`; override path with the "
                       "`MP_ECLAIM_GENERATOR_LOG` environment variable *(code: EclaimGenerator.rb:12)*\n")
        r = facts_overlap.article_overlap(p)
        self.assertEqual((r["bullets"], r["hi"], r["mid"]), (1, 1, 0))
        self.assertGreaterEqual(r["pairs"][0][0], facts_overlap.HI)

    def test_frontmatter_description_does_not_count_as_prose(self) -> None:
        p = self.write("# T\n\nThis article explains why generation never fails hard.\n\n"
                       "## Facts\n\n- Generator log file: `/tmp/EclaimGenerator-<uid>.log`; override path with the "
                       "`MP_ECLAIM_GENERATOR_LOG` environment variable *(code: EclaimGenerator.rb:12)*\n")
        r = facts_overlap.article_overlap(p)
        self.assertEqual((r["hi"], r["mid"]), (0, 0))

    def test_short_bullets_are_skipped(self) -> None:
        p = self.write("# T\n\nPort 8080 is the default listener for the server process.\n\n"
                       "## Facts\n\n- Port 8080\n")
        r = facts_overlap.article_overlap(p)
        self.assertEqual((r["bullets"], r["hi"], r["mid"]), (1, 0, 0))

    def test_no_facts_section_is_none(self) -> None:
        p = self.write("# T\n\nprose only\n")
        self.assertIsNone(facts_overlap.article_overlap(p))


if __name__ == "__main__":
    unittest.main()
