---
name: restructure-documentation
description: Audit and restructure an existing repository documentation system around explicit audiences, user journeys, canonical sources, ordered concepts, and preserved public interfaces. Use for bloated README files, overlapping guides, concepts introduced out of order, duplicated normative facts, broken navigation, or requests to reorganize an existing set of documents. Do not use for isolated corrections, documentation written from scratch, style-only editing, or AGENTS.md changes unless the user explicitly requests a normative restructuring of those operational instructions.
---

# Restructure Documentation

Improve the architecture of existing documentation, not merely its prose. Preserve the repository's language, conventions, facts, public navigation, and concurrent work while giving each audience a clear path to an outcome.

## Establish the boundary

1. Read repository instructions before inspecting or editing documentation. Treat `AGENTS.md` as operational instructions, not public documentation, unless the user explicitly asks for a normative change to it.
2. Inspect `git status --short`, relevant diffs, and recent history. Identify preexisting changes and protect them. Never rewrite or discard concurrent work to simplify the restructure.
3. State the documentation files authorized for writing, every protected file, the public paths and anchors, and any unresolved authority. Reading a file does not authorize editing it.
4. Inventory the requested documents and their inbound and outbound local links, headings, explicit HTML IDs, commands, examples, and factual claims.
5. Locate likely sources of truth throughout the repository. Inspect implementation, tests, configuration, build definitions, schemas, migrations, scripts, generated files, repository instructions, and history when they can establish the product's actual behavior.

Treat all investigation outside the accepted documentation scope as strictly read only. Never modify implementation, tests, configuration, build definitions, schemas, migrations, scripts, generated files, or documentation outside that scope. Apply this boundary independently of the repository's language, framework, and directory structure.

## Validate authority before writing

Validate the entire request against canonical repository sources before making the first edit:

1. Map every requested factual or normative claim to evidence for the existing behavior. Do not decide between contradictory facts without evidence.
2. Treat existing commands, options, arguments, exit semantics, formats, configuration keys, defaults, APIs, observable messages, installation processes, and release contracts as public contracts. Reorganize and clarify their documentation without inventing or changing them, and never edit the product to make it agree with a preferred documentation narrative.
3. Refuse the entire request before modifying any file if any part would invent or alter a public contract, modify a non-documentation file, present unconfirmed behavior as existing, or disguise a product change as documentation work. Do not apply an apparently safe documentation subset.

When the request contradicts confirmed behavior, preserve the product and refuse the request instead of changing the implementation.

When refusing, identify the conflict, cite the repository sources that establish the existing behavior, and explain that the requested outcome requires a separate product change. Suggest that follow-up when useful, but do not perform it.

When the repository cannot confirm a claim, state the uncertainty and ask for clarification or preserve the existing content. Never invent the missing fact. If the request requires presenting that unconfirmed claim as existing behavior, refuse atomically.

Resolve competing goals in this order:

1. Preserve existing public contracts and behavior.
2. Respect documentation-only writing authority.
3. Avoid unverified claims.
4. Improve documentation architecture, navigation, and prose.

## Model the documentation system

Read [documentation-roles.md](references/documentation-roles.md) when assigning roles or canonical ownership.

For each audience, record:

- where the reader starts;
- the outcome the reader needs;
- concepts and prerequisites required along the way;
- the canonical destination for each subject;
- the obstacle in the current journey.

Assign each document a primary role: landing page, conceptual guide, cookbook, normative reference, agent instruction, or historical record. A small document may combine compatible roles, but every subject must have one canonical owner. Prefer clarity of ownership and journey over arbitrary file count or length reduction.

Before moving content, create a subject inventory that names the current copies, authoritative evidence, intended owner, and interfaces to preserve. Treat file paths, headings used as fragments, explicit IDs, documented commands, factual examples, and stable terminology as public interfaces until evidence shows otherwise.

## Design the target journeys

Design from reader outcomes back to document boundaries:

1. Give every audience an obvious starting point.
2. Put the smallest concrete success before broad explanation.
3. Define a concept before the first step or claim that depends on it. In its canonical
   conceptual guide, make the definition heading and definition the first lexical
   occurrence of the term; do not use the term, including plural forms, in an
   introduction before defining it.
4. Show a concrete example before generalizing a rule.
5. Keep procedures in goal based recipes and exact facts in the normative reference.
6. Replace duplicated detail with enough context to choose a link, then link to the canonical owner.
7. Keep current guidance separate from historical rationale.

Preserve the language and established voice unless the user requests a change. Do not flatten purposeful differences between tutorial, explanation, recipe, and reference prose.

## Restructure safely

Make the smallest set of moves and edits that produces an observable structural gain.

- Preserve stable paths and anchors. If a heading must change, retain a compatible explicit HTML ID or use the repository's established redirect mechanism.
- Preserve verified commands, defaults, versions, examples, and other contracts exactly unless the authoritative source requires a correction.
- Edit around concurrent changes and re-read overlapping hunks immediately before applying a patch.
- Link to canonical details instead of maintaining partial copies.
- Avoid cosmetic rewrites that do not improve audience routing, ownership, ordering, or navigation.
- Stop with a grounded no-action result when the existing system already has coherent roles, journeys, ownership, ordering, and navigation.

When no action is justified, report the inspected documents, audience paths, canonical owners, interface checks, and validation evidence. Do not manufacture edits to demonstrate use of the skill.

## Validate the result

Validate from facts to journeys:

1. Compare commands, defaults, versions, and normative claims with their authoritative sources.
2. Check that protected files and concurrent changes remain intact.
3. Run the repository's own documentation checks.
4. Run the bundled local link validator:

   ```bash
   python3 .agents/skills/restructure-documentation/scripts/check_markdown_links.py <path>...
   ```

   When working from this skill's source directory, use `python3 restructure-documentation/scripts/check_markdown_links.py <path>...`. The command accepts Markdown files or directories, does not access external URLs, returns `0` when local navigation is valid, `1` for broken local links or fragments, and `2` for invalid input or read errors.

5. Inspect first occurrences of important terms, including inflected and plural forms,
   to confirm that each canonical conceptual guide defines the term before any
   introduction, summary, link text, step, or claim uses it.
6. Walk each audience journey from its actual entry point to its stated outcome, checking for circular routes and missing prerequisites.
7. Review the final diff for unintended prose churn, moved facts without an owner, broken paths or anchors, and edits outside scope.

Report structural changes by audience and canonical owner. Cite concrete paths, headings, and link destinations that demonstrate the resulting journeys, ownership, and concept order. List preserved interfaces, validation commands and results, and any ambiguity that remains; do not rely on an unsupported statement that a check passed.
