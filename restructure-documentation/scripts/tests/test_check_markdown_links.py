from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import check_markdown_links as validator


class MarkdownLinkValidatorTest(unittest.TestCase):
  def setUp(self):
    self.temporary = tempfile.TemporaryDirectory()
    self.root = Path(self.temporary.name)

  def tearDown(self):
    self.temporary.cleanup()

  def write(self, relative_path, content):
    path = self.root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path

  def run_main(self, *paths):
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
      exit_code = validator.main([str(path) for path in paths])
    return exit_code, stdout.getvalue(), stderr.getvalue()

  def test_accepts_relative_links_images_cross_file_fragments_and_html_ids(self):
    self.write("asset.png", "placeholder")
    self.write(
      "docs/guide.md",
      "# Guide\n\n## Repeated\n\n## Repeated\n\n"
      '<span id="manual-id"></span>\n',
    )
    readme = self.write(
      "README.md",
      "# Home\n\n"
      "[guide](docs/guide.md)\n"
      "[duplicate](docs/guide.md#repeated-1)\n"
      "[manual](docs/guide.md#manual-id)\n"
      "![asset](asset.png)\n"
      "[self](#home)\n",
    )

    exit_code, stdout, stderr = self.run_main(readme, self.root / "docs")

    self.assertEqual(0, exit_code)
    self.assertEqual("", stdout)
    self.assertEqual("", stderr)

  def test_reports_missing_paths_and_fragments_with_exit_one(self):
    broken = self.write(
      "broken.md",
      "# Broken\n\n[missing](absent.md)\n[fragment](#unknown)\n",
    )

    exit_code, stdout, stderr = self.run_main(broken)

    self.assertEqual(1, exit_code)
    self.assertIn("absent.md", stdout)
    self.assertIn("#unknown", stdout)
    self.assertEqual("", stderr)

  def test_ignores_external_links_and_links_in_fenced_or_inline_code(self):
    readme = self.write(
      "README.md",
      "# Home\n\n"
      "[web](https://example.test/missing)\n"
      "`[inline](absent.md)`\n"
      "```markdown\n[example](also-absent.md)\n```\n",
    )

    exit_code, stdout, stderr = self.run_main(readme)

    self.assertEqual(0, exit_code)
    self.assertEqual("", stdout)
    self.assertEqual("", stderr)

  def test_supports_reference_links_setext_headings_and_percent_encoding(self):
    self.write("a file.md", "Target\n======\n")
    readme = self.write(
      "README.md",
      "# Home\n\n[reference][target]\n\n"
      "[target]: <a%20file.md#target>\n",
    )

    exit_code, stdout, stderr = self.run_main(readme)

    self.assertEqual(0, exit_code)
    self.assertEqual("", stdout)
    self.assertEqual("", stderr)

  def test_returns_two_for_no_missing_or_non_markdown_input(self):
    invalid = self.write("notes.txt", "not Markdown")

    for arguments in ((), (self.root / "missing.md",), (invalid,)):
      with self.subTest(arguments=arguments):
        exit_code, stdout, stderr = self.run_main(*arguments)
        self.assertEqual(2, exit_code)
        self.assertEqual("", stdout)
        self.assertIn("error:", stderr)

  def test_returns_two_for_invalid_utf8(self):
    path = self.root / "broken.md"
    path.write_bytes(b"\xff")

    exit_code, stdout, stderr = self.run_main(path)

    self.assertEqual(2, exit_code)
    self.assertEqual("", stdout)
    self.assertIn("cannot read", stderr)


if __name__ == "__main__":
  unittest.main()
