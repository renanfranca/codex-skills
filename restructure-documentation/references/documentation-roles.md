# Documentation roles and canonical ownership

Read this reference when assigning responsibilities across an existing documentation set or deciding where duplicated material should live.

## Role matrix

| Role | Primary audience and outcome | Owns | Links to instead of duplicating | Warning sign |
| --- | --- | --- | --- | --- |
| Landing page | A new or returning reader choosing a path | Orientation, project promise, smallest successful start, route to next journeys | Conceptual depth, exhaustive recipes, full option tables | It becomes the only manual or forces every audience through one long page |
| Conceptual guide | A reader building a correct mental model | Vocabulary, relationships, invariants, reasons, boundaries | Step sequences and exhaustive parameter facts | It uses terms before defining them or becomes a command catalog |
| Cookbook | A user completing a concrete task | Goal based procedures, prerequisites, commands, expected outcomes, recovery | Repeated conceptual explanation and normative option inventories | Recipes are organized by implementation component rather than user outcome |
| Normative reference | A user or tool needing an exact fact | Complete commands, flags, configuration keys, schemas, defaults, compatibility, exit codes | Tutorials and persuasive explanation | The same normative fact has multiple owners |
| Agent instructions | An automated contributor operating in the repository | Operational constraints, required workflow, validation, safety boundaries | Public product guidance | `AGENTS.md` is presented as user documentation without an explicit normative request |
| Historical record | A maintainer reconstructing why or when something changed | Decisions, dated context, migrations, releases, superseded behavior | Current usage guidance and live normative rules | Readers must inspect history to learn the current contract |

One file may serve more than one role in a very small repository, but each subject still needs one identifiable canonical owner. Split a file when its audiences need incompatible reading orders, levels of detail, or maintenance authority. Do not split merely to make files shorter.

## Choose a canonical source

For each subject, select the owner that best satisfies these criteria, in order:

1. **Authority:** place normative facts where maintainers already verify or update that contract.
2. **Audience fit:** choose the document readers naturally consult for that outcome.
3. **Completeness:** keep the subject complete enough that partial copies are unnecessary.
4. **Stability:** prefer a path and anchor whose public use can be preserved.
5. **Maintenance locality:** keep facts close to the code, schema, or process that changes them when repository conventions support that relationship.

Record the choice before moving prose. Replace noncanonical detail with a short contextual sentence and a link to the owner. A link is not sufficient when the current document needs one fact to let the reader decide whether the destination is relevant.

## Map audiences and journeys

Build a compact inventory before editing:

| Audience | Starting point | Desired outcome | Required concepts | Canonical destinations | Current obstacle |
| --- | --- | --- | --- | --- | --- |
| Example: newcomer | Landing page | Complete first successful run | Workspace | Quick start, then concepts | The term “workspace” appears before definition |

Use the inventory to test the proposed structure:

- Every named audience has an obvious starting point.
- Each journey reaches a concrete outcome without circular navigation.
- Prerequisites and concepts appear before the step that depends on them.
- Examples demonstrate one concrete path before prose generalizes it.
- Normative facts have one owner and other documents link to it.
- Historical context does not override the current contract.

## Preserve interfaces while moving content

Treat file paths, inbound links, heading fragments, explicit HTML IDs, documented commands, examples relied on by tests, language, and factual claims as interfaces until evidence proves otherwise. Preserve an old heading or add an explicit compatible HTML ID when changing its title would break a public fragment. If a redirect mechanism exists, use it only when repository conventions make it reliable.

Do not silently reconcile contradictory facts. Identify the authoritative source from repository instructions, code, schemas, tests, and history; when authority remains unclear, stop and ask rather than choosing the most convenient wording.
