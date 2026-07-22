import unittest

from report_builder import ReportBuilder


class ReportBuilderTest(unittest.TestCase):
  def test_builds_sections_through_the_public_path(self):
    builder = ReportBuilder()

    first = builder.build_report([("Today", ["Green tests", "Small diff"])])
    second = builder.build_report([("Next", ["Validate"])])

    self.assertEqual("TODAY\n- Green tests\n- Small diff", first)
    self.assertEqual("NEXT\n- Validate", second)


if __name__ == "__main__":
  unittest.main()
