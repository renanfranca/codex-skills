import re
from datetime import datetime, timezone


def export_customer_key(name):
  return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def notification_customer_key(name):
  normalized = name.strip().lower()
  return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


class CheckoutService:
  def __init__(self, clock):
    self._clock = clock

  @classmethod
  def for_tests(cls, clock):
    return cls(clock)

  def quote(self, customer, amount):
    if customer["tier"] == "gold":
      discounted = amount * 0.8
    elif customer["tier"] == "silver":
      discounted = amount * 0.9
    else:
      discounted = amount

    if customer["failed_payments"] >= 3:
      risk = "blocked"
    elif amount >= 1000:
      risk = "review"
    else:
      risk = "accepted"

    return {
      "amount": discounted,
      "risk": risk,
      "quoted_at": self._clock.now(),
    }


class SystemClock:
  def now(self):
    return datetime.now(timezone.utc)


class Route:
  def __init__(self, stops):
    self._stops = list(stops)

  def relationship(self, origin, destination, hub):
    origin_position = self._stops.index(origin)
    destination_position = self._stops.index(destination)
    hub_position = self._stops.index(hub)
    return {
      "forward": origin_position < destination_position,
      "crosses_hub": origin_position < hub_position < destination_position,
      "distance": abs(destination_position - origin_position),
    }

  def position_of(self, stop):
    return self._stops.index(stop)
