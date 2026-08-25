# Design Review Rubric

This rubric is investigative, not a mechanical or exhaustive checklist. Apply a refactoring only when the finding has concrete evidence, removes a meaningful risk, and stays within the task scope.

## Contents

- [How to use the rubric](#how-to-use-the-rubric)
- [Temporal coupling](#temporal-coupling)
- [Hidden invocation state](#hidden-invocation-state)
- [Request state in long-lived objects](#request-state-in-long-lived-objects)
- [Side-effecting builders and factories](#side-effecting-builders-and-factories)
- [Metadata read at different times](#metadata-read-at-different-times)
- [Preformatted business diagnostics](#preformatted-business-diagnostics)
- [Interface syntax leaking into the domain](#interface-syntax-leaking-into-the-domain)
- [Redundant knowledge and repeated work](#redundant-knowledge-and-repeated-work)
- [Fragile mappings between models](#fragile-mappings-between-models)
- [Empty values used as workflow status](#empty-values-used-as-workflow-status)
- [Classes accumulating independent policies](#classes-accumulating-independent-policies)
- [Repeated searches hiding position](#repeated-searches-hiding-position)
- [Framework metadata in business types](#framework-metadata-in-business-types)
- [Abstractions created only for tests](#abstractions-created-only-for-tests)
- [Generic or primitive types hiding concepts](#generic-or-primitive-types-hiding-concepts)

## How to use the rubric

Start from changed behavior and its data flow. For a suspected issue, record the signal, the concrete failure or maintenance risk, and the invariant that a refactor would make explicit. Consider the false positives before classifying it. Prefer `No action` when evidence is weak, the current representation is already local and clear, or the refactor would exceed scope.

Select a coherent subset of improvements supported by the changed behavior and data flow. Classify and justify every finding that you change or materially report, but do not treat omissions in untouched code as review failures or manufacture a complete opportunity inventory. When the user explicitly requests an exhaustive review, inspect and classify every requested dimension. Preserve any reported finding in the final result when a public contract or authorization gate blocks it.

Separate observable contract from implementation representation. Preserve public behavior, types, errors, identity, ordering, and documented lifecycle. Do not preserve transport syntax, framework objects, internal storage, or helper topology merely because the current implementation exposes them internally. Likewise, do not route an independent operation through a new helper solely for reuse; require concrete risk in that operation and verify its complete semantics first.

## Temporal coupling

- **Signal:** one public operation works only after another method has been called in a particular order.
- **Risk:** valid-looking call sequences fail or rely on undocumented lifecycle knowledge.
- **Investigate:** Which state is established by the earlier call? Can the type be used before it is ready? Does the framework guarantee the sequence or merely happen to follow it?
- **Possible refactors:** construct required state eagerly, return a fully initialized value, or make phases explicit in separate types.
- **False positives:** a protocol may intentionally expose phases, and a framework callback order may be a stable contract.
- **Do not act when:** the ordering is explicit in the public protocol, enforced by types, and the extra abstraction would not reduce risk.

## Hidden invocation state

- **Signal:** an operation stores parse, request, or invocation data in fields and later helpers read it implicitly.
- **Risk:** reentrancy, repeated calls, concurrency, and isolated tests observe stale or cross-invocation data.
- **Investigate:** Is the field part of object identity or only one call? Can two calls overlap? Can the data travel as an immutable request or local context?
- **Possible refactors:** pass an immutable context, return an explicit result, or create a short-lived invocation object.
- **False positives:** caching immutable data derived solely from constructor arguments is not invocation state.
- **Do not act when:** the object's documented lifetime is exactly one invocation and construction enforces that lifetime.

## Request state in long-lived objects

- **Signal:** an application-scoped or otherwise reusable object retains values belonging to one request.
- **Risk:** data leaks between callers and behavior becomes timing-dependent.
- **Investigate:** What owns the lifecycle? Is the state mutated after construction? Is reuse concurrent or sequential?
- **Possible refactors:** move request data to method parameters, immutable request types, or correctly scoped objects.
- **False positives:** immutable configuration shared across requests is legitimate long-lived state.
- **Do not act when:** the container enforces a matching short scope and tests prove the intended lifecycle through public behavior.

## Side-effecting builders and factories

- **Signal:** a method named `build`, `create`, `spec`, or similar mutates its owner or changes later results.
- **Risk:** repeated construction is not idempotent and callers cannot reason locally about ownership.
- **Investigate:** Does a second call produce an independent complete value? Which hidden field changes? Is mutation essential to the constructed object?
- **Possible refactors:** build from immutable inputs, allocate a fresh builder, or return construction context explicitly.
- **False positives:** a conventional, short-lived mutable builder whose mutation is its explicit API.
- **Do not act when:** ownership is clear, the builder cannot escape, and repeated use is neither supported nor required.

## Metadata read at different times

- **Signal:** validation reads metadata and execution later reads the same source again.
- **Risk:** time-of-check/time-of-use divergence produces a plan validated against different facts.
- **Investigate:** Can the source change? Are transformations identical? Is consistency required for the whole operation?
- **Possible refactors:** capture one immutable snapshot and derive validation and execution from it.
- **False positives:** fresh reads are intentional when current state, rather than consistency, is the contract.
- **Do not act when:** the source is provably immutable for the operation or different-time semantics are explicit.

## Preformatted business diagnostics

- **Signal:** business or orchestration layers return complete user-facing sentences, punctuation, or rendering layout.
- **Risk:** presentation policy leaks inward and alternative interfaces must parse or duplicate messages.
- **Investigate:** What structured facts produced the message? Which layer owns localization, ordering, and formatting?
- **Possible refactors:** return typed problem facts and render them at the interface boundary.
- **False positives:** the exact text may itself be a contractual business artifact.
- **Do not act when:** no alternative presentation exists and the message is deliberately part of the stable domain language.

## Interface syntax leaking into the domain

- **Signal:** core types know option prefixes, HTTP field names, completion labels, UI widgets, or transport examples.
- **Risk:** changing one interface forces domain changes and prevents reuse through another adapter.
- **Investigate:** Is the value a real business term or only transport spelling? Who should translate it?
- **Possible refactors:** keep syntax in the primary adapter and map it to a domain concept.
- **False positives:** a user-visible identifier may genuinely be part of the ubiquitous language.
- **Do not act when:** the syntax is the business contract rather than an adapter representation.

## Redundant knowledge and repeated work

- **Signal:** a fact already established in the data flow is stored again as duplicated knowledge, representation, or state; recomputed through repeated computation, traversal, or transformation (including duplicated transformations); re-proved through repeated validation or defensive checks; or repaired downstream through late deduplication, normalization, or correction.
- **Risk:** multiple places appear authoritative, derived facts diverge or become stale, defensive branches obscure valid invariants, and consumers repeat policy that should have one owner.
- **Investigate:** Who established the fact, what is its authoritative source, and for how long does it remain valid? Did it cross a trust boundary? Can mutation or concurrency invalidate it? Do the representations or operations have independent ownership, lifecycle, or bounded-context policies? Which observable and public compatibility contracts depend on them? Would cheap local recomputation be simpler than cache, retained state, propagation, or a new abstraction?
- **Possible refactors:** carry an already validated or derived result forward, keep one authoritative representation or transformation, enforce normalization or uniqueness at the source, or remove only the downstream proof, defense, or repair demonstrated to be redundant.
- **False positives:** validation may be required again after persistence, deserialization, external input, or another trust boundary; defense in depth may be deliberate; similar work may express independently evolving policies; an identity field may have uses and lifecycle outside its container; and inexpensive recomputation may be clearer than shared state.
- **Do not act when:** the fact can become invalid, security or a trust boundary requires a fresh proof, ownership or bounded-context policy is independent, public compatibility relies on the representation, or removing repetition would add cache, coupling, state, or abstraction without a proportional reduction in risk.

## Fragile mappings between models

- **Signal:** conversion relies on matching names, ordinals, reflection, unchecked casts, or loosely typed maps.
- **Risk:** unrelated model evolution silently breaks another context.
- **Investigate:** What contract guarantees compatibility? Are unknown cases handled explicitly?
- **Possible refactors:** exhaustive mapping, a typed adapter, or a versioned translation boundary.
- **False positives:** generated models may share an authoritative schema with verified compatibility.
- **Do not act when:** compatibility is mechanically generated and enforced from the same source of truth.

## Empty values used as workflow status

- **Signal:** empty lists, strings, optionals, or maps mean both valid empty data and “not ready”, “not validated”, or “failed”.
- **Risk:** phases become indistinguishable and valid emptiness is misclassified.
- **Investigate:** Which states exist? Can callers observe an impossible combination? Is emptiness legitimate data?
- **Possible refactors:** model readiness, phase, or outcome explicitly with a result type or state enum.
- **False positives:** absence may be the complete and unambiguous domain meaning.
- **Do not act when:** empty has one documented meaning and no additional state must be represented.

## Classes accumulating independent policies

- **Signal:** one class makes decisions with distinct inputs, outputs, vocabulary, or reasons to change.
- **Risk:** unrelated policy changes interfere and the class becomes difficult to reason about as a unit.
- **Investigate:** Can each policy be named in domain language? Do they vary independently? Would extraction improve boundaries rather than just reduce size?
- **Possible refactors:** extract a pure policy object or domain service and keep orchestration explicit.
- **False positives:** several steps may form one cohesive invariant or transaction.
- **Do not act when:** separation would scatter one policy, expose internals, or add forwarding without an independent concept.

## Repeated searches hiding position

- **Signal:** several decisions repeatedly call membership and position searches on the same ordered data.
- **Risk:** intent is obscured and cost or inconsistent “not found” handling is repeated.
- **Investigate:** Is position a stable concept for the operation? Are duplicate values possible? Does order carry business meaning?
- **Possible refactors:** build one immutable value-to-position index or introduce an ordering value.
- **False positives:** collections are tiny and each search has a different semantic condition.
- **Do not act when:** indexing complicates duplicate semantics or yields no clarity beyond a single lookup.
- **Independent operations:** limit a consolidation to the operation with demonstrated repeated-search risk. Reuse it from a separate direct lookup only when that lookup has its own concrete risk and the change preserves identity, equality, duplicate, ordering, and not-found behavior.

## Framework metadata in business types

- **Signal:** core types carry annotations, descriptors, reflection objects, framework callbacks, or configuration nodes.
- **Risk:** the business model becomes coupled to technical lifecycle and representation changes.
- **Investigate:** Which facts are actually needed? Can an adapter translate metadata into an immutable business value?
- **Possible refactors:** introduce a boundary mapper or a domain-facing snapshot containing only relevant facts.
- **False positives:** some annotations are compile-time markers with no runtime dependency or behavior.
- **Do not act when:** the type is intentionally an integration type located at the boundary.

## Abstractions created only for tests

- **Signal:** a production overload, factory, interface, or setter is used only by tests and bypassed by runtime composition.
- **Risk:** production API expands without a business or architectural purpose and tests validate an unreal path.
- **Investigate:** What observable behavior needs control? Can it be exercised through the production seam? Is the abstraction a meaningful runtime capability?
- **Possible refactors:** connect the seam to production, test at a stable boundary, or remove the test-only abstraction.
- **False positives:** clocks, random sources, and external capabilities are valid production dependencies even when tests exploit them heavily.
- **Do not act when:** the seam represents a genuine nondeterministic or external dependency used by runtime code.

## Generic or primitive types hiding concepts

- **Signal:** unrelated strings, booleans, numbers, maps, or `Object` values are interchangeable despite different meanings or constraints.
- **Risk:** invalid combinations cross boundaries and validation is scattered.
- **Investigate:** Does the value have domain-specific rules, identity, units, lifecycle, or terminology? Would a type remove a real invalid state?
- **Possible refactors:** introduce a value object, enum, discriminated union, or typed collection at the appropriate boundary.
- **False positives:** a local primitive with obvious meaning and no independent rules may be clearest.
- **Do not act when:** the new type would only rename data without enforcing, communicating, or composing a meaningful concept.
