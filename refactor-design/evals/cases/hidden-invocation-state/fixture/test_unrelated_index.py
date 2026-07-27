import unittest

from unrelated_index import UnrelatedIndex


class UnrelatedIndexTest(unittest.TestCase):
  def test_builds_the_unrelated_index(self):
    index = UnrelatedIndex()

    self.assertEqual({"a": 0, "b": 1}, index.build(["a", "b"]))
    self.assertEqual({"next": 0}, index.build(["next"]))


if __name__ == "__main__":
  unittest.main()
