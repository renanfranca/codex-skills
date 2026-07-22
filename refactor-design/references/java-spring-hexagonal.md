# Java, Spring, and Hexagonal Design Review

Use this reference only after the general rubric when the reviewed scope uses Java, Spring, or hexagonal architecture. Treat every item as an investigation, not a mandatory pattern.

## Contents

- [Spring singleton state](#spring-singleton-state)
- [Framework lifecycle and temporal coupling](#framework-lifecycle-and-temporal-coupling)
- [Constructor injection and object lifetime](#constructor-injection-and-object-lifetime)
- [Records and defensive copies](#records-and-defensive-copies)
- [Optional.get and explicit invariants](#optionalget-and-explicit-invariants)
- [Object as a business value](#object-as-a-business-value)
- [Enums across bounded contexts](#enums-across-bounded-contexts)
- [Cross-context adapters](#cross-context-adapters)
- [Domain ports and technical seams](#domain-ports-and-technical-seams)
- [Composition before Spring](#composition-before-spring)
- [Presentation and technical metadata](#presentation-and-technical-metadata)
- [Executable architecture rules](#executable-architecture-rules)

## Spring singleton state

Spring components are singleton-scoped by default. Inspect mutable fields that hold parsed arguments, request values, current project data, accumulators, or invocation-specific lookup tables. These fields can leak data between calls even when the framework normally invokes the component sequentially.

Prefer immutable constructor dependencies plus method-local request state. If an invocation needs several derived values, pass one immutable context or create a short-lived object explicitly. Do not flag immutable configuration caches or thread-safe caches merely because they are fields; prove that the value belongs to one invocation.

## Framework lifecycle and temporal coupling

Framework callbacks can hide ordering dependencies. Trace whether a public method depends on a prior callback, specification builder, post-construction hook, or parser mutation. A framework guarantee can make the sequence valid, but it does not automatically make the object safe for reuse, direct invocation, or tests.

Prefer construction that yields a usable object, independent specifications, or explicit phase types. Keep the existing lifecycle when it is a documented stable contract and another abstraction would only mirror the framework.

## Constructor injection and object lifetime

Use constructor injection to make stable dependencies explicit and keep one intentional construction shape. Match dependency lifetime to ownership: singleton services should depend on stateless collaborators or appropriately scoped providers, not retain request objects.

Do not introduce interfaces, alternate constructors, setters, or factories solely to shorten tests. A seam is justified when it models a real runtime capability, an external dependency, or nondeterminism and is wired through production.

## Records and defensive copies

Java records are shallowly immutable. A record that accepts a mutable `List`, `Set`, `Map`, array, or mutable framework object can still change after construction.

Investigate whether immutability is an invariant or merely assumed. Use defensive copies such as `List.copyOf` at the ownership boundary when callers must not mutate the value. Do not copy blindly when the type intentionally exposes a live view or the collection is already proven immutable.

## Optional.get and explicit invariants

An unchecked `Optional.get()` is acceptable only when a nearby, visible invariant makes presence unavoidable. Otherwise it converts a missing business case into a technical exception.

Prefer branching, `orElseThrow` with a meaningful exception, or a domain result that represents absence. Do not replace every `get()` mechanically when a prior exhaustive branch or constructor invariant already proves presence.

## Object as a business value

`Object` in an application or domain model often hides an unbounded set of accepted values, serialization assumptions, or casts. Trace every producer and consumer before changing it.

Prefer a generic parameter, sealed hierarchy, typed value, or boundary conversion when the accepted variants have business meaning. Keep `Object` inside a technical integration envelope when the framework genuinely owns the payload and business code does not inspect it.

## Enums across bounded contexts

Do not rely on `Target.valueOf(source.name())`, ordinals, or identical labels between independently evolving contexts. Use an exhaustive adapter mapping so additions fail visibly and translation policy has one owner.

Name-based mapping can be reasonable for generated types sharing one authoritative schema and a validation mechanism that guarantees parity. Record that contract rather than assuming coincidental names.

## Cross-context adapters

When one bounded context consumes another context's application service or model directly, inspect whether business rules are being coupled across orchestration boundaries. Translate through an adapter owned by the consuming boundary when the contexts have independent language or evolution.

A secondary adapter may wrap another context's public application API when it implements a domain capability. Avoid inventing a domain port for an in-memory technical detail that has no domain meaning; use an ordinary technical seam at the composition boundary instead.

## Domain ports and technical seams

A domain port names a capability the domain needs without describing its mechanism. It belongs with the domain language and is implemented by infrastructure. A technical seam exists to isolate a framework, clock, parser, or construction concern and need not be promoted to a domain concept.

Review names and dependencies rather than suffixes alone. Do not create a port merely to satisfy a layering diagram or a mock-based test. Prefer the smallest boundary that expresses ownership and prevents inward infrastructure dependencies.

## Composition before Spring

Manual composition is appropriate when objects must operate before a Spring context exists. Keep that composition explicit and narrowly responsible for wiring primary, application, domain, and secondary components.

Once Spring is active, prefer ordinary Spring-managed construction and constructor injection. Do not let a `composition` package become a service locator or a shortcut for mixing business and infrastructure responsibilities.

## Presentation and technical metadata

Domain types should carry structured facts, not CLI option spelling, HTTP field names, help descriptions, completion candidates, framework descriptors, or preformatted diagnostics unless those are genuine business concepts.

Translate interface input in primary adapters and external metadata in secondary adapters. When one metadata schema governs validation and later execution, consider one immutable domain-facing snapshot to prevent inconsistent reads. Keep presentation rendering at the primary boundary.

## Executable architecture rules

Promote a rule to ArchUnit, Checkstyle, or an architecture test when it is objective, stable, and mechanically detectable. Good candidates include forbidden package dependencies, annotation placement, naming constraints, and framework imports crossing a boundary.

Keep judgment-heavy heuristics in review guidance. Temporal coupling, service cohesion, meaningful value objects, and appropriate ports usually require context and produce too many false positives for a blanket automated rule. Test observable behavior at public boundaries; do not add tests whose sole purpose is asserting internal class topology.
