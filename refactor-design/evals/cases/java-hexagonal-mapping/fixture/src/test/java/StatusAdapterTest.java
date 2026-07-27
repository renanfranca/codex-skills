import adapter.StatusAdapter;
import billing.BillingStatus;
import sales.OrderStatus;
import schema.GeneratedParityMapper;
import schema.GeneratedSource;
import schema.GeneratedTarget;

public final class StatusAdapterTest {
  public static void main(String[] arguments) {
    StatusAdapter adapter = new StatusAdapter();
    require(adapter.toBilling(OrderStatus.NEW) == BillingStatus.NEW);
    require(adapter.toBilling(OrderStatus.SHIPPED) == BillingStatus.SHIPPED);

    GeneratedParityMapper generated = new GeneratedParityMapper();
    require(generated.map(GeneratedSource.ALPHA) == GeneratedTarget.ALPHA);
    require(generated.map(GeneratedSource.BETA) == GeneratedTarget.BETA);
  }

  private static void require(boolean condition) {
    if (!condition) {
      throw new AssertionError("mapping contract failed");
    }
  }
}
