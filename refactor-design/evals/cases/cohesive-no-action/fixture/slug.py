import re


def slug(text):
  normalized = text.strip().lower()
  return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
