package schema;

// Both enums are generated from schema/status.json, whose generator verifies parity.
public final class GeneratedParityMapper {
  public GeneratedTarget map(GeneratedSource source) {
    return GeneratedTarget.valueOf(source.name());
  }
}
