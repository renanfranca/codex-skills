import unittest

from report_builder import export_customer_key, notification_customer_key


class CustomerKeyTest(unittest.TestCase):
  def test_both_public_paths_share_the_same_customer_key_contract(self):
    names = [" Acme, Inc. ", "North & South", "Already-Safe"]

    self.assertEqual(
      ["acme-inc", "north-south", "already-safe"],
      [export_customer_key(name) for name in names],
    )
    self.assertEqual(
      ["acme-inc", "north-south", "already-safe"],
      [notification_customer_key(name) for name in names],
    )


if __name__ == "__main__":
  unittest.main()
