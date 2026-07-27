import unittest

from lifecycle import (
  Catalog,
  DraftRenderer,
  ExplicitPhaseProtocol,
  MetadataRunner,
  TextBuilder,
)


class StableMetadata:
  def read(self):
    return {"version": "2"}


class LifecycleTest(unittest.TestCase):
  def test_renders_repeatedly_through_the_public_path(self):
    renderer = DraftRenderer()

    self.assertEqual("TODAY\n- green", renderer.render("Today", ["green"]))
    self.assertEqual("NEXT\n- ship", renderer.render("Next", ["ship"]))

  def test_runs_against_one_stable_metadata_source(self):
    self.assertEqual("release-2", MetadataRunner(StableMetadata()).run())

  def test_explicit_protocol_enforces_its_documented_phases(self):
    protocol = ExplicitPhaseProtocol()
    with self.assertRaisesRegex(RuntimeError, "not open"):
      protocol.close()
    protocol.open()
    protocol.close()

  def test_short_lived_builder_and_catalog_are_publicly_usable(self):
    self.assertEqual("ab", TextBuilder().add("a").add("b").build())
    self.assertTrue(Catalog([" Alpha "]).contains("alpha"))


if __name__ == "__main__":
  unittest.main()
