"""Regression tests for the resume PDF rendering pipeline's level-3
heading pre-Typst rewrite ("Title | Dates" / "Title | Org, Location |
Dates" -> #entry-heading[...] / #entry-heading-3[...]), which avoids a
Typst-side content-to-string() round trip that silently drops spaces
adjacent to em-dashes/parens/umlauts in heading titles (GitHub issue #1).

Uses only synthetic placeholder data -- no candidate/application content.

These tests run the REAL pandoc against the REAL template/resume.typ,
then apply the sed expressions extracted directly from build.sh's own
post-processing block (not a hand-maintained duplicate) -- so this file
stays in sync with build.sh automatically if that block ever changes.

Deliberately NOT included: an end-to-end invocation of build.sh itself.
build.sh's own tempfile line ("mktemp -t resume-build") is a separate,
already-tracked portability issue on GNU/Windows sed environments,
unrelated to the heading-spacing fix under test here -- invoking build.sh
directly on such an environment would fail there first, for a reason this
file isn't testing, before ever reaching the sed logic below. Once that
separate mktemp fix lands, an end-to-end smoke test can be added.

Skips cleanly if pandoc/typst/sed are not available.

Run with: py -m unittest test_resume_rendering
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
TEMPLATE = REPO_ROOT / "template" / "resume.typ"
BUILD_SH = REPO_ROOT / "build.sh"

_MISSING_TOOLS = [
    name for name in ("pandoc", "typst", "sed") if shutil.which(name) is None
]


def _extract_sed_expressions() -> list[str]:
    """Pull the exact -e expressions out of build.sh's post-processing
    sed block, so this test always exercises build.sh's real current
    logic instead of a separately hand-maintained copy of it."""
    text = BUILD_SH.read_text(encoding="utf-8")
    match = re.search(r"sed -E -i\.bak\b(.*?)\"\$tmp_typ\"", text, re.DOTALL)
    assert match, "could not locate the sed -E -i.bak post-processing block in build.sh"
    exprs = re.findall(r"-e '([^']*)'", match.group(1))
    assert len(exprs) == 4, f"expected 4 -e expressions in build.sh, found {len(exprs)}"
    return exprs


def _render_typst_source(markdown_body: str) -> str:
    """Run real pandoc (with the real template/resume.typ) on a synthetic
    markdown snippet, then apply build.sh's real, freshly-extracted sed
    expressions -- returns the resulting Typst source text. Writes only
    to an isolated temp directory; never touches applications/, tracker
    data, or build.sh/template/resume.typ themselves."""
    front_matter = "---\nname: Test Person\ncontact: Test City, XX\n---\n\n"
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_path = Path(tmp_dir) / "snippet.md"
        md_path.write_text(front_matter + markdown_body, encoding="utf-8")
        typ_path = Path(tmp_dir) / "snippet.typ"
        subprocess.run(
            [
                "pandoc", str(md_path),
                "--from=markdown",
                f"--template={TEMPLATE}",
                "--wrap=none",
                "--to=typst",
                "--output", str(typ_path),
            ],
            check=True, cwd=REPO_ROOT, capture_output=True, text=True,
        )
        sed_argv = ["sed", "-E"]
        for expr in _extract_sed_expressions():
            sed_argv += ["-e", expr]
        sed_argv.append(str(typ_path))
        result = subprocess.run(sed_argv, check=True, capture_output=True, text=True, encoding="utf-8")
        return result.stdout


class ResumeHeadingSpacingTests(unittest.TestCase):
    def setUp(self):
        if _MISSING_TOOLS:
            self.skipTest(f"required tool(s) not available on PATH: {', '.join(_MISSING_TOOLS)}")

    def test_two_part_heading_preserves_spacing_and_dashes(self):
        md = (
            "## Ausbildung\n\n"
            "### Test University Alpha (TUA) \u2014 Grundstudium Testfach | 2018 \u2013 2020\n\n"
            "- Placeholder bullet.\n"
        )
        out = _render_typst_source(md)
        self.assertIn(
            "#entry-heading[Test University Alpha (TUA) --- Grundstudium Testfach][2018 -- 2020]",
            out,
        )
        # The auto-generated pandoc label for this heading must be gone.
        self.assertNotIn("<test-university-alpha", out)

    def test_two_part_heading_preserves_umlauts_parens_and_ampersand(self):
        md = (
            "## Ausbildung\n\n"
            "### Universit\u00e4t M\u00fcnchen (LMU) \u2014 Grundstudium & Recht | 2018 \u2013 2020\n\n"
            "- Placeholder bullet.\n"
        )
        out = _render_typst_source(md)
        self.assertIn(
            "#entry-heading[Universit\u00e4t M\u00fcnchen (LMU) --- Grundstudium & Recht][2018 -- 2020]",
            out,
        )
        self.assertNotIn("<universit", out)

    def test_three_part_heading_splits_correctly(self):
        md = (
            "## Erfahrung\n\n"
            "### Senior Engineer | Acme Corp, Berlin | 2020 \u2013 2022\n\n"
            "- Placeholder bullet.\n"
        )
        out = _render_typst_source(md)
        self.assertIn(
            "#entry-heading-3[Senior Engineer][Acme Corp, Berlin][2020 -- 2022]",
            out,
        )
        self.assertNotIn("<senior-engineer", out)
        # Must never fall through to the 2-part rule (which would wrongly
        # swallow the first pipe into the title itself).
        self.assertNotIn("#entry-heading[Senior Engineer", out)

    def test_heading_without_pipe_is_untouched(self):
        md = "## Sonstiges\n\n### Heading ohne Pipe\n\n- Placeholder bullet.\n"
        out = _render_typst_source(md)
        # Isolate this test's own generated body -- everything from its
        # unique section marker onward -- instead of searching the whole
        # file. The template's boilerplate always contains the #let
        # entry-heading(...) / #let entry-heading-3(...) function
        # DEFINITIONS regardless of input, so a whole-file substring check
        # for "#entry-heading" would false-positive on those definitions
        # even when no heading was actually converted into a call of one.
        marker = "== Sonstiges"
        self.assertIn(marker, out)
        body = out[out.index(marker):]
        self.assertIn("=== Heading ohne Pipe", body)
        # Its own pandoc label must survive untouched -- proves rule 2 is
        # scoped only to headings that actually contain a pipe.
        self.assertIn("<heading-ohne-pipe>", body)
        self.assertNotIn("#entry-heading[", body)
        self.assertNotIn("#entry-heading-3[", body)

    def test_role_line_paragraph_transformation_still_works(self):
        md = (
            "## Erfahrung\n\n"
            "### Some Company \u2014 Some City\n\n"
            "**Some Role** | Jan 2020 \u2013 Feb 2021\n\n"
            "- Placeholder bullet.\n"
        )
        out = _render_typst_source(md)
        self.assertIn("#role-line[Some Role][Jan 2020 -- Feb 2021]", out)


if __name__ == "__main__":
    unittest.main()
