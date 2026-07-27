import ast
from pathlib import Path


tree = ast.parse(Path("report_builder.py").read_text(encoding="utf-8"))
instance_writes = []
for node in ast.walk(tree):
  targets = []
  if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
    targets = (
      node.targets
      if isinstance(node, ast.Assign)
      else [node.target]
    )
  for target in targets:
    for nested in ast.walk(target):
      if (
        isinstance(nested, ast.Attribute)
        and isinstance(nested.value, ast.Name)
        and nested.value.id == "self"
      ):
        instance_writes.append(nested.attr)

if instance_writes:
  raise SystemExit(
    "ReportBuilder still stores invocation progress on the instance: "
    + ", ".join(sorted(set(instance_writes)))
  )
