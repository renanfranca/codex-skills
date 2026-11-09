---
name: notion-dev-tasks
description: Consult, add, update, or complete development tasks on the fixed Notion page Pendências de desenvolvimento only when the user explicitly invokes $notion-dev-tasks. A mention of a pending task alone does not activate this skill.
---

# Notion development tasks

Manage the existing page [Pendências de desenvolvimento](https://www.notion.so/413b2aa0430681ab9921c146e3da80c1), page ID `413b2aa0430681ab9921c146e3da80c1`. Use this fixed destination without asking where to save or creating a replacement page or database.

## Invocation and scope

Apply this workflow only to an explicitly invoked request and the follow-ups needed to finish that request. A previous invocation does not authorize managing tasks in later unrelated work. Do not activate it because someone merely mentions a bug, possible issue, or pending task.

Managing a task does not authorize performing its underlying work, running reproductions, installing tools, or publishing an issue. Completing a task requires an explicit user request to mark it complete; an apparently successful result alone is insufficient.

Write task titles, summaries, and new explanatory prose in Brazilian Portuguese. Preserve technical identifiers, commands, code, diagnostics, URLs, and relevant original source excerpts. Keep hypotheses and inconclusive results clearly labeled. Never invent deadlines, results, or verification.

## Read and resolve

1. Identify the operation, project, and task from the request and available conversation. Read files the user indicates when needed to capture their substance. Do not execute the task described in those files. Ask only when essential information is missing or materially different interpretations remain.
2. Use the connected Notion plugin tools. Fetch the fixed page before consulting or changing tasks. Check for truncated content or omitted blocks and obtain the relevant content before relying on it. If the target item or its details remain incomplete, report the limitation and do not edit that item.
3. For additions and updates, compare existing entries in both `Pendentes` and `Concluídas` by project and intended action, not just exact title. Update a clearly matching pending entry instead of duplicating it. If several entries could match, ask which one the user means before writing. If an update or completion has no match, report that and clarify rather than creating an entry. If an addition matches a completed task, clarify whether the user intends a new task or to reopen it.
4. Before writing page content, read `notion://docs/notion-flavored-markdown-spec` through the Notion resource interface or the Notion `fetch` tool using that URI as `id`. Never pass it to a web fetch tool. Follow the current specification and tool instructions rather than guessing syntax.

## Operations

### Consult

Return the requested tasks, filtered by project or status as requested, with the useful current situation and next action. If no items match, say so. Do not write, reorganize, check boxes, or create sections during a consultation.

### Add

Add an unchecked checkbox under `Pendentes`. Use a concrete action in the title with the form **Projeto: ação concreta**. Keep `Situação` and `Próxima ação` visible outside collapsed details. Add `Concluir quando` only when the request or evidence establishes a completion condition.

Put extensive context and evidence in a native Notion toggle associated with the item. Match the surrounding page style; the current page uses a checkbox, visible paragraphs, and a following toggle as one logical task. The following is a structural example, not a task to save:

```markdown
- [ ] **Projeto: ação concreta**

**Situação:** resumo do estado conhecido, incluindo incertezas.

**Próxima ação:** ação necessária para retomar o trabalho.

<toggle>
Contexto e evidências

Contexto suficiente para retomar, com exemplos e evidências relevantes.
</toggle>
```

Include the relevant substance of supplied files in the details, not only their paths. Preserve reproducible examples, exact versions and commands, diagnostics, source references, and distinctions between observations and suspected causes. A temporary path may be recorded as provenance but must not be the only way to recover essential context. Do not copy unrelated private content or credentials.

### Update

Amend the uniquely identified item in place. Update the visible situation and next action when the new information warrants it, and add relevant evidence inside its details. Preserve earlier context, examples, and links; distinguish historical evidence from newer results rather than silently overwriting it. Do not mark complete or move sections unless explicitly requested.

### Complete

On an explicit completion request, check the box and move the entire logical item from `Pendentes` to `Concluídas`: checkbox, visible paragraphs, completion condition if present, and all associated toggles and details. Record the supplied outcome, including any remaining uncertainty, without claiming tests or checks that were not reported. If no outcome is supplied or established by the conversation, state `Resultado: conclusão solicitada pelo usuário; resultado não informado.` Do not invent a successful verification.

If the item is already complete, report that state and add only any newly requested outcome. Do not duplicate it. Replace a section's empty-state text such as `Nenhuma por enquanto.` only when adding its first real item; preserve unrelated content.

## Targeted changes and recovery

Use the smallest uniquely matching `update_content` edits supported by the Notion update tool. Preserve all other items, links, sections, nesting, and native references. Do not replace the whole page when targeted edits suffice. If a needed section is absent, add only that section as part of an authorized write.

For completion, prefer one update containing the source removal and destination insertion. If the tool requires separate writes, save the complete destination item successfully before removing the source. After a partial move, reconcile the actual saved state before continuing so no details are lost or duplicated.

If access fails, report the inaccessible destination and what could not be read or saved. Do not claim success, silently save elsewhere, or create a replacement. If a write fails, times out, returns warnings, or has an uncertain outcome, fetch the current state before retrying. Reconcile with the intended edit and retry only the missing change when the state is clear. If access or the saved state remains uncertain, stop and tell the user what remains unsaved or unconfirmed.

After a successful change, return a short summary and the page link. Open the page with the Notion page panel when available. A clean successful write needs no extra fetch solely for verification; fetch when resolving warnings, uncertainty, or a next edit that needs the exact saved state.
