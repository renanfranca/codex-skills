import unittest

from report_builder import ReportBuilder


class ReportBuilderTest(unittest.TestCase):
  def test_builds_report_repeatedly_through_public_path(self):
    builder = ReportBuilder()

    self.assertEqual("- one\n- two", builder.build_report(["one", "two"]))
    self.assertEqual("- next", builder.build_report(["next"]))


if __name__ == "__main__":
  unittest.main()
