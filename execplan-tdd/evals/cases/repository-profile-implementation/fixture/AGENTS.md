# Repository workflow

All code changes use `$execplan-tdd`.

- ExecPlan destination: `.plans/<YYYY-MM-DD>_<TYPE>_<short-kebab-title>-exec-plan.md`
- Relevant suite for each TDD cycle: `python3 -m unittest -q`
- Public checkpoint: `python3 public_check.py`
- Final validation: `python3 -m unittest -q`, `python3 docs_check.py`, and `python3 public_check.py`
- Canonical documentation sources: `README.md`, `api-schema.json`, and root `CONTRIBUTING.md`

Treat `.generated/` as a disposable projection. Never edit it.
