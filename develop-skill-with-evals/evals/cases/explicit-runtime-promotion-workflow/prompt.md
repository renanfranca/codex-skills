Update only the authorized temporary `sample-skill/scripts/render.py` so its renderer removes surrounding whitespace before converting text to uppercase. Do not edit `sample-skill/SKILL.md`. `sample-baseline` is the unchanged comparison source.

Classify the change, then use `./audit-runner` in this order:

1. Plan the diagnostic workflow and save it as `diagnostic-plan.json`.
2. Run `probe-change` once and save it as `diagnostic.json`.
3. Plan the promotion workflow and save it as `promotion-plan.json`.
4. Run `validate-change` once and save it as `validation.json`.

Declare `gpt-5.6-sol` with `medium` reasoning effort for the executor and `gpt-5.6-terra` with `medium` reasoning effort for the judge on all four commands. Use `./fake-codex` as the Codex command for executed operations, keep each model session authorization proportional to its displayed plan, save pure JSON standard output, and do not commit or publish.
