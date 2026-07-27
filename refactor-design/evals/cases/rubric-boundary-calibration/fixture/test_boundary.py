import unittest

from boundary import (
  Batch,
  CustomerFilter,
  FrameworkField,
  SourcePriority,
  TargetPriority,
  audit_phrase,
  display_line,
  map_priority,
  parse_cli_filter,
  validate_import,
)


class BoundaryTest(unittest.TestCase):
  def test_renders_public_import_diagnostics(self):
    self.assertEqual("Import failed: no rows were supplied.", validate_import([]))
    self.assertEqual("Import ready.", validate_import([{"id": 1}]))

  def test_parses_cli_filter_at_the_public_boundary(self):
    active = {"active": True}
    archived = {"active": False}

    self.assertTrue(parse_cli_filter("--active").accepts(active))
    self.assertTrue(parse_cli_filter("--archived").accepts(archived))
    self.assertIsInstance(parse_cli_filter("--active"), CustomerFilter)

  def test_maps_context_priorities(self):
    self.assertIs(TargetPriority.LOW, map_priority(SourcePriority.LOW))
    self.assertIs(TargetPriority.HIGH, map_priority(SourcePriority.HIGH))

  def test_exposes_current_batch_status_and_business_metadata(self):
    self.assertEqual([], Batch().status())
    descriptor = {"external_name": "customer", "widget": "text"}
    field = FrameworkField(descriptor)
    self.assertEqual("customer", field.business_name())

  def test_preserves_deliberate_simple_contracts(self):
    self.assertEqual("Approved by Ada", audit_phrase("Ada"))
    self.assertEqual("7: ready", display_line(7, "ready"))


if __name__ == "__main__":
  unittest.main()
