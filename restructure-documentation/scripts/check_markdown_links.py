#!/usr/bin/env python3
"""Validate local Markdown links and GitHub-style fragments without network access."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


MARKDOWN_SUFFIXES = {".md", ".markdown"}
INLINE_LINK = re.compile(
  r"!?\[[^\]]*\]\(\s*(?:<([^>\n]+)>|([^\s)\n]+))(?:\s+['\"(][^)\n]*[)'\"])?\s*\)"
)
REFERENCE_USE = re.compile(r"!?\[([^\]]+)\]\[([^\]]*)\]")
REFERENCE_DEFINITION = re.compile(
  r"^\s{0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))",
  re.MULTILINE,
)
HTML_LINK = re.compile(
  r"<(?:a|img)\b[^>]*?\b(?:href|src)\s*=\s*(['\"])(.*?)\1",
  re.IGNORECASE,
)
HTML_ID = re.compile(
  r"<(?:[A-Za-z][\w:-]*)\b[^>]*?\b(?:id|name)\s*=\s*(['\"])(.*?)\1",
  re.IGNORECASE,
)
ATX_HEADING = re.compile(r"^\s{0,3}(#{1,6})[ \t]+(.+?)\s*$")
SETEXT_UNDERLINE = re.compile(r"^\s{0,3}(=+|-+)\s*$")
HTML_TAG = re.compile(r"<[^>]+>")
MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]+\)")
MARKDOWN_LINK_TEXT = re.compile(r"\[([^\]]+)\]\([^)]+\)")
MARKDOWN_DECORATION = re.compile(r"[*_~`]")


@dataclass(frozen=True)
class Link:
  source: Path
  line: int
  destination: str


class InputError(Exception):
  pass


def github_slug(text: str) -> str:
  text = HTML_TAG.sub("", text)
  text = MARKDOWN_IMAGE.sub(r"\1", text)
  text = MARKDOWN_LINK_TEXT.sub(r"\1", text)
  text = MARKDOWN_DECORATION.sub("", text)
  text = text.strip().casefold()
  text = "".join(
    character
    for character in text
    if character.isalnum() or character in {" ", "-", "_"}
  )
  return re.sub(r"\s+", "-", text)


def visible_lines(text: str) -> list[tuple[int, str]]:
  lines = []
  fenced = False
  fence_character = ""
  fence_length = 0
  for number, line in enumerate(text.splitlines(), start=1):
    fence = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
    if fence:
      marker = fence.group(1)
      if not fenced:
        fenced = True
        fence_character = marker[0]
        fence_length = len(marker)
      elif marker[0] == fence_character and len(marker) >= fence_length:
        fenced = False
      continue
    if not fenced:
      lines.append((number, line))
  return lines


def anchors_for(text: str) -> set[str]:
  anchors = set()
  slug_counts: dict[str, int] = {}
  lines = visible_lines(text)

  for _, line in lines:
    for match in HTML_ID.finditer(line):
      anchors.add(match.group(2))

  index = 0
  while index < len(lines):
    _, line = lines[index]
    heading = ATX_HEADING.match(line)
    heading_text = None
    if heading:
      heading_text = re.sub(r"[ \t]+#+[ \t]*$", "", heading.group(2))
    elif index + 1 < len(lines):
      current_number, current_line = lines[index]
      next_number, next_line = lines[index + 1]
      if next_number == current_number + 1 and SETEXT_UNDERLINE.match(next_line):
        heading_text = current_line.strip()
        index += 1
    if heading_text is not None:
      base = github_slug(heading_text)
      duplicate = slug_counts.get(base, 0)
      anchor = base if duplicate == 0 else f"{base}-{duplicate}"
      slug_counts[base] = duplicate + 1
      anchors.add(anchor)
    index += 1
  return anchors


def strip_inline_code(line: str) -> str:
  return re.sub(r"`+[^`]*`+", "", line)


def links_for(path: Path, text: str) -> list[Link]:
  definitions = {}
  for match in REFERENCE_DEFINITION.finditer(text):
    definitions[match.group(1).strip().casefold()] = match.group(2) or match.group(3)

  links = []
  for line_number, raw_line in visible_lines(text):
    line = strip_inline_code(raw_line)
    for match in INLINE_LINK.finditer(line):
      links.append(Link(path, line_number, match.group(1) or match.group(2)))
    for match in HTML_LINK.finditer(line):
      links.append(Link(path, line_number, match.group(2)))
    for match in REFERENCE_USE.finditer(line):
      label = (match.group(2) or match.group(1)).strip().casefold()
      if label in definitions:
        links.append(Link(path, line_number, definitions[label]))
  return links


def markdown_files(inputs: list[str]) -> list[Path]:
  if not inputs:
    raise InputError("at least one Markdown file or directory is required")

  files = set()
  for raw_path in inputs:
    path = Path(raw_path)
    if not path.exists():
      raise InputError(f"input does not exist: {path}")
    if path.is_dir():
      try:
        files.update(
          candidate
          for candidate in path.rglob("*")
          if candidate.is_file() and candidate.suffix.casefold() in MARKDOWN_SUFFIXES
        )
      except OSError as error:
        raise InputError(f"cannot read directory {path}: {error}") from error
    elif path.is_file() and path.suffix.casefold() in MARKDOWN_SUFFIXES:
      files.add(path)
    else:
      raise InputError(f"input is not a Markdown file or directory: {path}")
  return sorted((path.resolve() for path in files), key=str)


def read_markdown(path: Path) -> str:
  try:
    return path.read_text(encoding="utf-8")
  except (OSError, UnicodeError) as error:
    raise InputError(f"cannot read {path}: {error}") from error


def is_external(destination: str) -> bool:
  if destination.startswith("//"):
    return True
  scheme = urlsplit(destination).scheme.casefold()
  return bool(scheme) and scheme not in {"file"}


def resolve_target(source: Path, raw_path: str) -> Path:
  decoded = unquote(raw_path)
  if decoded.startswith("/"):
    return (Path.cwd() / decoded.lstrip("/")).resolve()
  return (source.parent / decoded).resolve()


def validate(files: list[Path]) -> list[str]:
  texts = {path: read_markdown(path) for path in files}
  anchor_cache = {path: anchors_for(text) for path, text in texts.items()}
  failures = []

  for source, text in texts.items():
    for link in links_for(source, text):
      destination = link.destination.strip()
      if not destination or is_external(destination):
        continue
      parsed = urlsplit(destination)
      target = source if not parsed.path else resolve_target(source, parsed.path)
      fragment = unquote(parsed.fragment)

      if not target.exists():
        failures.append(
          f"{source}:{link.line}: missing local target: {link.destination}"
        )
        continue
      if fragment:
        if target.is_dir():
          failures.append(
            f"{source}:{link.line}: cannot validate fragment on directory: "
            f"{link.destination}"
          )
          continue
        if target.suffix.casefold() not in MARKDOWN_SUFFIXES:
          continue
        if target not in anchor_cache:
          try:
            target_text = read_markdown(target)
          except InputError as error:
            failures.append(f"{source}:{link.line}: {error}")
            continue
          anchor_cache[target] = anchors_for(target_text)
        if fragment not in anchor_cache[target]:
          failures.append(
            f"{source}:{link.line}: missing fragment #{fragment} in {target}"
          )
  return failures


def parse_args(arguments: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description=(
      "Check local links, images, and Markdown fragments. "
      "External URLs are not accessed."
    )
  )
  parser.add_argument("paths", nargs="*", help="Markdown files or directories")
  return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
  options = parse_args(sys.argv[1:] if arguments is None else arguments)
  try:
    files = markdown_files(options.paths)
    failures = validate(files)
  except InputError as error:
    print(f"error: {error}", file=sys.stderr)
    return 2

  for failure in failures:
    print(failure)
  return 1 if failures else 0


if __name__ == "__main__":
  raise SystemExit(main())
