#!/usr/bin/env python3
"""Authenticated local operator client; credentials stay in process memory."""
import argparse
import http.cookiejar
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.request


def request(op, args=None):
  log = Path.home() / ".dsh/web-runtime.log"
  opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
  deadline = time.monotonic() + 25
  while True:
    urls = re.findall(r"dsh web: (http://127\.0\.0\.1:3080/\?token=\S+)", log.read_text())
    try:
      if not urls:
        raise urllib.error.URLError('No current launch URL')
      with opener.open(urls[-1], timeout=5) as response:
        response.read()
      break
    except urllib.error.URLError:
      if time.monotonic() >= deadline:
        raise RuntimeError('DSH did not become ready; inspect its private runtime log') from None
      time.sleep(0.25)
  data = json.dumps({"op": op, "args": args or {}}).encode()
  req = urllib.request.Request("http://127.0.0.1:3080/api/dsh-workflow/console", data=data,
    headers={"Content-Type": "application/json", "Origin": "http://127.0.0.1:3080"})
  try:
    with opener.open(req, timeout=60) as response:
      result = json.load(response)
  except urllib.error.HTTPError as error:
    try:
      result = json.load(error)
    except (ValueError, UnicodeError):
      raise RuntimeError('DSH operator request failed, HTTP ' + str(error.code)) from None
  if not result["ok"]:
    raise RuntimeError(result["error"])
  return result["value"]


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("operation")
  parser.add_argument("--args", default="{}", help="JSON arguments, never credentials")
  options = parser.parse_args()
  if options.operation == "session.history":
    parser.error("Full history contains reasoning; use an inspection script that selects safe fields")
  print(json.dumps(request(options.operation, json.loads(options.args)), indent=2))


if __name__ == "__main__":
  main()
