import unittest

from pricing import total


class PricingTest(unittest.TestCase):
  def test_nonmember_total_is_unchanged(self):
    self.assertEqual(total(1000), 1000)


if __name__ == "__main__":
  unittest.main()
