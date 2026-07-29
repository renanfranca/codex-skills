import unittest

from pricing import total


class PricingTest(unittest.TestCase):
  def test_total(self):
    self.assertEqual(total(1000), 1000)
