package adapter;

import billing.BillingStatus;
import sales.OrderStatus;

public final class StatusAdapter {
  public BillingStatus toBilling(OrderStatus source) {
    return BillingStatus.valueOf(source.name());
  }
}
