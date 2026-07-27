import unittest

from cohesion import (
  CheckoutService,
  Route,
  export_customer_key,
  notification_customer_key,
)


class FixedClock:
  def now(self):
    return "2026-07-27T12:00:00Z"


class CohesionTest(unittest.TestCase):
  def test_keeps_customer_keys_consistent(self):
    name = " North & South "
    self.assertEqual("north-south", export_customer_key(name))
    self.assertEqual("north-south", notification_customer_key(name))

  def test_quotes_through_one_public_orchestration_path(self):
    service = CheckoutService(FixedClock())
    quote = service.quote(
      {"tier": "gold", "failed_payments": 0},
      1200,
    )

    self.assertEqual(960, quote["amount"])
    self.assertEqual("review", quote["risk"])
    self.assertEqual("2026-07-27T12:00:00Z", quote["quoted_at"])

  def test_describes_route_relationships_and_one_direct_lookup(self):
    route = Route(["A", "H", "B"])

    self.assertEqual(
      {"forward": True, "crosses_hub": True, "distance": 2},
      route.relationship("A", "B", "H"),
    )
    self.assertEqual(1, route.position_of("H"))


if __name__ == "__main__":
  unittest.main()
