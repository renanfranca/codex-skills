from pathlib import Path
import re


adapter = Path("src/main/java/adapter/StatusAdapter.java").read_text(encoding="utf-8")
generated = Path(
  "src/main/java/schema/GeneratedParityMapper.java"
).read_text(encoding="utf-8")

if "valueOf" in adapter or ".name()" in adapter:
  raise SystemExit("cross-context adapter still relies on matching names")
if "switch" not in adapter:
  raise SystemExit("cross-context adapter does not use an exhaustive switch")
for source, target in (("NEW", "BillingStatus.NEW"), ("SHIPPED", "BillingStatus.SHIPPED")):
  pattern = rf"\b{source}\b\s*->\s*{re.escape(target)}\b"
  if not re.search(pattern, adapter):
    raise SystemExit(f"cross-context adapter does not map {source} explicitly")
if "GeneratedTarget.valueOf(source.name())" not in generated:
  raise SystemExit("generated shared-schema counterexample was changed")
