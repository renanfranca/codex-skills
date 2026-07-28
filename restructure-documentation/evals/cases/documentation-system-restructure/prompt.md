Audit and restructure this existing documentation set for three audiences: a newcomer installing Lantern, an operator looking for recipes, and a contributor needing exact configuration facts. The current files overlap and introduce concepts out of order.

Maintain the required living ExecPlan at `documentation-restructure-execplan.md`.

Preserve the existing file paths, the public `README.md#getting-started` and `docs/reference.md#config-file` anchors, the commands `lantern init` and `lantern scan --format json`, the environment variable `LANTERN_CACHE_DIR`, and the fact that configuration schema version 3 is current. Do not edit `AGENTS.md`. Validate all local documentation navigation after the restructure.

In the conceptual guide, make the `## Workspace` definition the first occurrence of `workspace`, including its plural form. Do not use the term in an introduction before that definition.

In the final evidence, cite the exact resulting headings and link destinations that route each audience, identify the canonical owner for concepts, procedures, and configuration facts, show where `workspace` is defined before procedural use, and cite where each preserved anchor and fact remains. Do not merely state that validation passed.
