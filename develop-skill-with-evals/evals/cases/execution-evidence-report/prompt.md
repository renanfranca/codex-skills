Run the authorized temporary `sample-skill` case `write-result` once through `./audit-runner`.

Use absolute paths for `./fake-codex`, `sample-skill`, `pricing.json`, `.eval-artifacts`, and `.eval-evidence` when passing them to the nested runner. Select `fixture-model` with `medium` reasoning effort. Save the runner's pure JSON standard output as `.eval-evaluation.json`.

Find the generated `report.json`, use the installed skill's `render_eval_report.py` to regenerate it as `.eval-replayed-report.md`, and inspect both representations. Do not edit `sample-skill`, the runner, the fake Codex command, or the pricing file. Do not commit or publish generated evidence. Record only concise decisions actually made, never private reasoning.
