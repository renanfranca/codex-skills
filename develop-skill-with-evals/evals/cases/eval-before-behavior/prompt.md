Update `target-skill` so it refuses to summarize input containing an explicit `PRIVATE` marker. Build the behavior through evaluations and leave the workspace uncommitted.

After creating the focused evaluation but before changing skill behavior, run `python3 audit_eval_sequence.py baseline`. Exit code 1 is the required RED; stop without implementing if it exits 0. After implementing the behavior, run `python3 audit_eval_sequence.py candidate` and require exit code 0. Keep the generated `evaluation-evidence.json`.
