# Scorecard

Apply this fixed 100-point scorecard to every pinned result. Do not introduce discretionary bonus points, reward raw test count or production LOC, normalize scores to force separation, or break a tie subjectively.

## Seed4J effectiveness — 35 points

| Criterion | Points | Full-credit evidence |
| --- | ---: | --- |
| Discovery and help | 5 | Observed CLI/runtime version, global help/catalog, and relevant module help before selection. |
| Preflight and plan | 8 | Read-only plan performed before apply; dependency, provider, path, parameter-source, and Git states were evaluated. |
| Module choice and order | 8 | Selected modules fit the specification and were applied in a dependency-safe, economical sequence. |
| Explicit parameters | 7 | Required and reproducibility-relevant values were supplied explicitly rather than left ambiguous. |
| Reproducible history and wrapper | 7 | `.seed4j/modules`, coherent module commits, and the appropriate build wrapper are present and usable. |

Award partial credit only for independently evidenced portions. A successful build does not prove planning or discovery occurred.

## Specification correctness — 30 points

- Allocate 27 points equally among the numbered requirements frozen from `SPEC.md`. Test each through the public observation surface and retain enough precision for the subtotal to equal 27 exactly.
- Award 3 points for the exact public contract, including signature/entrypoint and specified error behavior. When the SPEC has no error case, use the complete caller-visible contract rather than inventing one.

Source inspection can explain failures but cannot replace an executable public acceptance result when execution is feasible.

## Test quality — 20 points

| Criterion | Points | Full-credit evidence |
| --- | ---: | --- |
| Native verification | 6 | The repository's complete native verification command succeeds at the pinned implementation. |
| Requirement coverage | 8 | Native tests exercise every frozen specification requirement through behavior-facing APIs. |
| Boundary and failure coverage | 3 | Tests cover relevant invalid, negative, edge, or interaction cases established by the SPEC. |
| Enforced coverage gate | 3 | The build enforces a meaningful automated coverage threshold; a generated report alone is insufficient. |

Do not award points for the number of tests itself. Duplication and implementation-coupled tests can justify deductions within the applicable criterion.

## Design and reproducibility — 15 points

| Criterion | Points | Full-credit evidence |
| --- | ---: | --- |
| Separation and clarity | 6 | Responsibilities are cohesive, names reveal intent, and behavior can be understood without reconstructing hidden state. |
| Boundary robustness | 4 | Parsing and interactions remain correct at specification boundaries and relevant combinations. |
| Minimal public state/API | 3 | Only the caller-visible surface required by the SPEC is exposed; mutable public state is absent. |
| Conventional layout | 2 | Sources, tests, build metadata, and wrapper follow the generated ecosystem's conventional structure. |

## Comparisons and deductions

For every non-full criterion, name the exact lost points and link the evidence. Use identical deduction rules across runs. Keep original precision in calculations and round only displayed totals consistently.

Show same-model effort groups and same-effort model groups before the aggregate ranking. If only one member exists, omit that group and say why. Keep ties as ties and order tied rows by declared execution index, not preference.

Treat timing, token/cost data, transcript size/format, code/test size, raw test count, and unrequested robustness experiments as unweighted appendices. State unavailable data as unavailable, never as zero.
