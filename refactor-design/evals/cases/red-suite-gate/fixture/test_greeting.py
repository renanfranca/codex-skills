import unittest

from greeting import greeting


class GreetingTest(unittest.TestCase):
  def test_uses_the_requested_punctuation(self):
    self.assertEqual("Hello, Ada!", greeting("Ada"))


if __name__ == "__main__":
  unittest.main()
