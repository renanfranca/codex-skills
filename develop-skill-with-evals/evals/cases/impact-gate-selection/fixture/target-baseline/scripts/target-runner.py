#!/usr/bin/env python3
import json
import sys


print(json.dumps({"status": "ok"}), file=sys.stderr)
