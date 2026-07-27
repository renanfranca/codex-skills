import re


def export_customer_key(name):
  return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def notification_customer_key(name):
  normalized = name.strip().lower()
  return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
