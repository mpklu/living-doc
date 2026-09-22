"""build-facts: ## Facts → facts/<area>.md; ## In plain terms → guide/<area>.md;
plain-terms bullets with identifiers or tags fail."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build_facts  # noqa: E402


def cli(*args: str) -> int:
    with contextlib.redirect_stdout(io.StringIO()):
        return build_facts.cli_main(list(args))


def art(plain: str) -> str:
    return ("---\nupdated: 2026-01-01\narea: cda\n---\n# T\n\nprose\n\n"
            "## Facts\n\n- Port `4444` is the ICD listener *(code: `CDACommunication.m:12`)*\n\n"
            f"## In plain terms\n\n{plain}\n")


class BuildFactsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.k = Path(self.tmp.name) / "knowledge"
        (self.k / "concepts/cda").mkdir(parents=True)
        self.a = self.k / "concepts/cda/x.md"

    def test_both_renderings_from_one_article(self) -> None:
        self.a.write_text(art("- If a claim says 'sent, forwarding failed', the office's Digital ID has usually expired."), encoding="utf-8")
        self.assertEqual(cli("--knowledge-dir", str(self.k)), 0)
        facts = (self.k / "facts/cda.md").read_text(encoding="utf-8")
        guide = (self.k / "guide/cda.md").read_text(encoding="utf-8")
        self.assertIn("CDACommunication.m", facts)
        self.assertNotIn("CDACommunication.m", guide)
        self.assertIn("Digital ID has usually expired", guide)
        self.assertIn("in plain terms", guide)
        self.assertEqual(cli("--knowledge-dir", str(self.k), "--check"), 0)

    def test_plain_terms_with_identifier_fails(self) -> None:
        self.a.write_text(art("- Check `CDACommunication.m` when it fails *(code: x)*"), encoding="utf-8")
        self.assertEqual(cli("--knowledge-dir", str(self.k)), 1)
        self.assertFalse((self.k / "guide/cda.md").exists())

    def test_no_plain_section_no_guide(self) -> None:
        self.a.write_text(art("").replace("## In plain terms\n\n\n", ""), encoding="utf-8")
        self.assertEqual(cli("--knowledge-dir", str(self.k)), 0)
        self.assertFalse((self.k / "guide").exists())


if __name__ == "__main__":
    unittest.main()
