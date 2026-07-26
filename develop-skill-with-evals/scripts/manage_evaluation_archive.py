#!/usr/bin/env python3
"""Rebuild or validate a permanent evaluation report archive."""

import argparse
import json
from pathlib import Path

from evaluation_archive import rebuild_archive, validate_archive


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  subparsers = parser.add_subparsers(dest="operation", required=True)
  for operation in ("rebuild", "validate"):
    command = subparsers.add_parser(operation)
    command.add_argument("--archive", type=Path, required=True)
  args = parser.parse_args()
  if args.operation == "rebuild":
    result = rebuild_archive(args.archive.resolve())
  else:
    result = validate_archive(args.archive.resolve())
  print(json.dumps(result, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
