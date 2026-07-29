import json
from pathlib import Path


readme = Path("README.md").read_text(encoding="utf-8").lower()
schema = json.loads(Path("api-schema.json").read_text(encoding="utf-8"))

assert "member" in readme
assert "10 percent" in readme
assert schema["total"]["parameters"]["member"]["type"] == "boolean"
assert schema["total"]["parameters"]["member"]["default"] is False
