import os
from pathlib import Path
import subprocess
import sys
import tempfile


skill_dir = Path(os.environ["SKILL_EVAL_SKILL_DIR"])
script = skill_dir / "scripts" / "check_markdown_links.py"
if not script.is_file():
  print("validator script is missing", file=sys.stderr)
  raise SystemExit(1)


def run(*paths):
  return subprocess.run(
    [sys.executable, str(script), *map(str, paths)],
    capture_output=True,
    text=True,
    check=False,
  )


with tempfile.TemporaryDirectory() as temporary:
  root = Path(temporary)
  (root / "image.png").write_bytes(b"not-a-real-png")
  (root / "guide.md").write_text(
    "# Guide\n\n"
    "## Repeated\n\n"
    "## Repeated\n\n"
    '<a id="manual-target"></a>\n',
    encoding="utf-8",
  )
  (root / "README.md").write_text(
    "# Home\n\n"
    "[guide](guide.md)\n"
    "[second duplicate](guide.md#repeated-1)\n"
    "[manual](guide.md#manual-target)\n"
    "![image](image.png)\n"
    "[local](#home)\n",
    encoding="utf-8",
  )
  valid = run(root)
  if valid.returncode != 0:
    print(valid.stdout, valid.stderr, file=sys.stderr)
    raise SystemExit(1)

  (root / "broken.md").write_text(
    "# Broken\n\n"
    "[missing path](absent.md)\n"
    "[missing fragment](guide.md#absent)\n",
    encoding="utf-8",
  )
  broken = run(root / "broken.md")
  if broken.returncode != 1:
    print("broken links must return 1", broken.stdout, broken.stderr, file=sys.stderr)
    raise SystemExit(1)
  if "absent.md" not in broken.stdout or "#absent" not in broken.stdout:
    print("broken link output is not actionable", broken.stdout, file=sys.stderr)
    raise SystemExit(1)

  invalid = run(root / "not-markdown.txt")
  if invalid.returncode != 2:
    print("invalid input must return 2", invalid.stdout, invalid.stderr, file=sys.stderr)
    raise SystemExit(1)

  missing = run(root / "does-not-exist")
  if missing.returncode != 2:
    print("missing input must return 2", missing.stdout, missing.stderr, file=sys.stderr)
    raise SystemExit(1)
