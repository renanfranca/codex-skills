#!/usr/bin/env node

import fs from "node:fs";

function fail(message) {
  process.stderr.write(`${message}\n`);
  process.exit(1);
}

function readJson(path, label) {
  try {
    return JSON.parse(fs.readFileSync(path, "utf8"));
  } catch {
    fail(`Could not read ${label}.`);
  }
}

function normalizedAccounts(registry) {
  if (!registry || !Array.isArray(registry.accounts)) {
    fail("The codex-auth registry has an unsupported shape.");
  }
  const accounts = registry.accounts.map((account) => {
    const accountKey = String(account?.account_key ?? "");
    const email = String(account?.email ?? "").trim();
    const alias = String(account?.alias ?? "").trim();
    const accountName = String(account?.account_name ?? "").trim();
    const plan = String(account?.plan ?? "").trim();
    if (!accountKey || !email || /[\t\r\n]/.test(accountKey + email + alias + accountName + plan)) {
      fail("A registered account is missing safe identifying metadata.");
    }
    return { account_key: accountKey, email, alias, account_name: accountName, plan };
  });
  return {
    active_account_key: String(registry.active_account_key ?? ""),
    accounts,
  };
}

function findByKey(registry, key) {
  return registry.accounts.find((account) => account.account_key === key);
}

function assertUniqueSelectors(accounts, registry) {
  for (const account of accounts) {
    const query = account.email.toLowerCase();
    const matches = registry.accounts.filter((candidate) =>
      [candidate.email, candidate.alias, candidate.account_name].some((value) =>
        value.toLowerCase().includes(query),
      ),
    );
    if (matches.length !== 1) {
      fail(`The email selector for ${account.email} is ambiguous in the codex-auth registry.`);
    }
  }
}

function emitRows(accounts) {
  for (const account of accounts) {
    process.stdout.write(
      `${account.account_key}\t${account.email}\t${account.alias}\t${account.plan}\n`,
    );
  }
}

function activeAccount(registry) {
  const active = findByKey(registry, registry.active_account_key);
  if (!active) {
    fail("The active account is not present in the codex-auth registry.");
  }
  emitRows([active]);
}

function existingPair(configPath, registry) {
  const config = readJson(configPath, "the existing switcher configuration");
  const oldA = config?.accounts?.["account-a"] ?? config?.accounts?.["conta-a"];
  const oldB = config?.accounts?.["account-b"] ?? config?.accounts?.["conta-b"];
  const accountA = findByKey(registry, String(oldA?.account_key ?? ""));
  const accountB = findByKey(registry, String(oldB?.account_key ?? ""));
  if (!accountA || !accountB || accountA.account_key === accountB.account_key) {
    fail("The existing account mapping cannot be adopted safely.");
  }
  if (accountA.email.toLowerCase() === accountB.email.toLowerCase()) {
    fail("The existing account mapping contains duplicate emails.");
  }
  assertUniqueSelectors([accountA, accountB], registry);
  emitRows([accountA, accountB]);
}

function suggestedPair(registry) {
  if (registry.accounts.length !== 2) {
    fail("Automatic selection requires exactly two registered accounts.");
  }
  const active = findByKey(registry, registry.active_account_key);
  if (!active) {
    fail("The active account is not present in the codex-auth registry.");
  }
  const other = registry.accounts.find(
    (account) => account.account_key !== active.account_key,
  );
  if (active.email.toLowerCase() === other.email.toLowerCase()) {
    fail("The registered accounts have duplicate emails and cannot be switched unambiguously.");
  }
  assertUniqueSelectors([active, other], registry);
  emitRows([active, other]);
}

function selectedPair(registry, firstIndex, secondIndex) {
  const first = Number(firstIndex);
  const second = Number(secondIndex);
  if (
    !Number.isInteger(first) ||
    !Number.isInteger(second) ||
    first < 1 ||
    second < 1 ||
    first > registry.accounts.length ||
    second > registry.accounts.length ||
    first === second
  ) {
    fail("Select two different account numbers from the displayed list.");
  }
  const pair = [registry.accounts[first - 1], registry.accounts[second - 1]];
  if (pair[0].email.toLowerCase() === pair[1].email.toLowerCase()) {
    fail("The selected accounts have duplicate emails and cannot be switched unambiguously.");
  }
  assertUniqueSelectors(pair, registry);
  emitRows(pair);
}

const [command, registryPath, ...args] = process.argv.slice(2);
if (!command || !registryPath) {
  fail("Usage: registry-helper.mjs <list|active|existing-pair|suggested-pair|selected-pair> <registry> [...]");
}

const registry = normalizedAccounts(readJson(registryPath, "the codex-auth registry"));

switch (command) {
  case "list":
    registry.accounts.forEach((account, index) => {
      const marker = account.account_key === registry.active_account_key ? "active" : "inactive";
      const suffix = account.alias ? `, ${account.alias}` : "";
      process.stdout.write(`${index + 1}. ${account.email} (${account.plan || "unknown"}${suffix}, ${marker})\n`);
    });
    break;
  case "active":
    activeAccount(registry);
    break;
  case "existing-pair":
    if (!args[0]) fail("existing-pair requires a configuration path.");
    existingPair(args[0], registry);
    break;
  case "suggested-pair":
    suggestedPair(registry);
    break;
  case "selected-pair":
    selectedPair(registry, args[0], args[1]);
    break;
  default:
    fail("Unknown registry-helper command.");
}
