from enum import Enum


def validate_import(rows):
  if not rows:
    return "Import failed: no rows were supplied."
  return "Import ready."


class CustomerFilter:
  def __init__(self, option):
    if option not in {"--active", "--archived"}:
      raise ValueError(option)
    self.option = option

  def accepts(self, customer):
    return customer["active"] is (self.option == "--active")


def parse_cli_filter(option):
  return CustomerFilter(option)


class SourcePriority(Enum):
  LOW = 1
  HIGH = 2


class TargetPriority(Enum):
  LOW = "low"
  HIGH = "high"


def map_priority(source):
  return TargetPriority[source.name]


class Batch:
  def __init__(self):
    self.errors = []

  def status(self):
    return self.errors


class FrameworkField:
  def __init__(self, descriptor):
    self.descriptor = descriptor

  def business_name(self):
    return self.descriptor["external_name"]


def audit_phrase(actor):
  return f"Approved by {actor}"


def display_line(line_number, text):
  return f"{line_number}: {text}"
