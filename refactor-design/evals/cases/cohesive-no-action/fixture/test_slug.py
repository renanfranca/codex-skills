import unittest

from slug import slug


class SlugTest(unittest.TestCase):
  def test_normalizes_user_visible_slug(self):
    self.assertEqual("small-green-change", slug(" Small, green change! "))


if __name__ == "__main__":
  unittest.main()
