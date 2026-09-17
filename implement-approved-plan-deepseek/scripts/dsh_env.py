#!/usr/bin/env python3
"""Manage the standalone DSH Web service and its private Tailscale endpoint."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from dsh_console import request

HOME = Path('/home/renanfranca')
ROOT = ['/mnt/c/Windows/System32/wsl.exe', '-d', 'Ubuntu-Seed4J', '-u', 'root', '--exec']


def run(argv, capture=False, check=True):
  return subprocess.run(argv, text=True, capture_output=capture, check=check)


def tailnet():
  result = run(['tailscale', 'status', '--json'], capture=True, check=False)
  return json.loads(result.stdout) if result.stdout else {}


def remote_start():
  state = tailnet()
  if state.get('BackendState') != 'Running':
    print('Tailscale login pending. Run: tailscale up --hostname=renan-dsh --accept-dns=false')
    if state.get('AuthURL'):
      print('Login: ' + state['AuthURL'])
    return
  run(['tailscale', 'serve', '--bg', '--https=443', 'http://127.0.0.1:3080'])
  print('Private Web: https://' + state['Self']['DNSName'].rstrip('.') + '/')


def open_url(remote=True, session=None):
  urls = re.findall(r'dsh web: (http://127\.0\.0\.1:3080/\?token=\S+)', (HOME/'.dsh/web-runtime.log').read_text())
  if not urls:
    raise RuntimeError('Start DSH first')
  url = urls[-1]
  if remote:
    state = tailnet()
    if state.get('BackendState') != 'Running':
      raise RuntimeError('Tailscale login is still pending')
    url = url.replace('http://127.0.0.1:3080', 'https://' + state['Self']['DNSName'].rstrip('.'))
  # Launch URL is an access credential. Display only on this explicit operator command.
  print(url)
  if session:
    print('After login, open session ' + session + ' in the sidebar.')


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('command', choices=['start', 'stop', 'restart', 'status', 'doctor', 'open', 'sessions', 'workspaces', 'resume'])
  parser.add_argument('session_id', nargs='?')
  parser.add_argument('--local', action='store_true')
  args = parser.parse_args()
  if args.command in ['start', 'restart']:
    run(ROOT + ['systemctl', args.command, 'tailscaled'])
    run(ROOT + ['systemctl', args.command, 'dsh-web'])
    remote_start()
  elif args.command == 'stop':
    run(['tailscale', 'serve', '--https=443', 'off'], check=False)
    run(ROOT + ['systemctl', 'stop', 'dsh-web'])
  elif args.command in ['status', 'doctor']:
    state = tailnet()
    print('DSH service: ' + run(['systemctl', 'is-active', 'dsh-web'], capture=True, check=False).stdout.strip())
    print('Tailscale: ' + str(state.get('BackendState', 'unavailable')))
    print('Full Access: native danger-full-access, approval never; Unix user renanfranca')
    if state.get('Self', {}).get('DNSName'):
      print('Private Web: https://' + state['Self']['DNSName'].rstrip('.') + '/')
    if args.command == 'doctor':
      print(json.dumps(request('catalog'), indent=2))
      run(['tailscale', 'serve', 'status'], check=False)
      for command in [['java', '-version'], ['habit-hooks', '--version'], ['pmd', '--version'], ['docker', 'version', '--format', '{{.Server.Version}}']]:
        run(command, check=False)
  elif args.command == 'open':
    open_url(not args.local, args.session_id)
  elif args.command == 'sessions':
    rows = request('session.list')['items']
    print(json.dumps([{'sessionId': row['sessionId'], 'title': row.get('projections', {}).get('values', {}).get('title'),
      'running': row['running'], 'cwd': row['cwd']} for row in rows], indent=2))
  elif args.command == 'workspaces':
    print(json.dumps(request('workspace.list'), indent=2))
  elif args.command == 'resume':
    if not args.session_id:
      parser.error('resume requires a session ID')
    print(json.dumps(request('session.resume', {'sessionId': args.session_id}), indent=2))
    print('Resume preserves conversation and permissions. For a workflow, ask its original Coordinator to call workflow_resume.')


if __name__ == '__main__':
  try:
    main()
  except Exception as error:
    print(str(error), file=sys.stderr)
    sys.exit(1)
