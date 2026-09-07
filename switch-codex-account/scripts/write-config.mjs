#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

function required(name) {
  const value = process.env[name];
  if (!value) {
    process.stderr.write(`Missing configuration value: ${name}\n`);
    process.exit(1);
  }
  return value;
}

const outputPath = process.argv[2];
if (!outputPath) {
  process.stderr.write("Usage: write-config.mjs <output-path>\n");
  process.exit(1);
}

const config = {
  schema_version: 1,
  distro: required("SWITCHER_CONFIG_DISTRO"),
  codex_home_linux: required("SWITCHER_CONFIG_CODEX_HOME_LINUX"),
  codex_home_windows: required("SWITCHER_CONFIG_CODEX_HOME_WINDOWS"),
  node_linux: required("SWITCHER_CONFIG_NODE_LINUX"),
  codex_auth_js_linux: required("SWITCHER_CONFIG_CODEX_AUTH_JS_LINUX"),
  codex_auth_version: "codex-auth 0.2.10",
  app_package_name: "OpenAI.Codex",
  app_id: "App",
  graceful_timeout_seconds: 15,
  startup_delay_seconds: 5,
  accounts: {
    "account-a": {
      label: "Account A",
      selector: required("SWITCHER_CONFIG_ACCOUNT_A_EMAIL"),
      account_key: required("SWITCHER_CONFIG_ACCOUNT_A_KEY"),
      configured: true,
    },
    "account-b": {
      label: "Account B",
      selector: required("SWITCHER_CONFIG_ACCOUNT_B_EMAIL"),
      account_key: required("SWITCHER_CONFIG_ACCOUNT_B_KEY"),
      configured: true,
    },
  },
};

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
const temporary = `${outputPath}.${process.pid}.tmp`;
fs.writeFileSync(temporary, `${JSON.stringify(config, null, 2)}\n`, {
  encoding: "utf8",
  mode: 0o600,
});
fs.renameSync(temporary, outputPath);
