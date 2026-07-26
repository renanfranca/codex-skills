# Model evaluation comparison

- Reports: `18`
- Observations: `18`
- Executed observations: `18`
- Interpretation: directional pilot, not statistical proof.

| Model | PASS | Observations | Qualifies | Input tokens | Output tokens | Reasoning output | Duration ms | API reference |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| gpt-5.6-luna | 6 | 6 | no | 2311093 | 33837 | 6499 | 763390 | unavailable |

## gpt-5.6-luna

- `explicit-runtime-promotion-workflow`: 3/3 PASS, stable `true`
- `load-skill-creator-first`: 3/3 PASS, stable `false`
- Explanation complete ratio: `1.0`
- Explanation coherent ratio: `0.833333`
- Base-rate API reference: `0.708931`
- Long context indeterminate observations: `5`
| gpt-5.6-sol | 6 | 6 | no | 5832476 | 57114 | 14251 | 1649465 | unavailable |

## gpt-5.6-sol

- `explicit-runtime-promotion-workflow`: 3/3 PASS, stable `true`
- `load-skill-creator-first`: 3/3 PASS, stable `false`
- Explanation complete ratio: `1.0`
- Explanation coherent ratio: `0.666667`
- Base-rate API reference: `6.483352`
- Long context indeterminate observations: `6`
| gpt-5.6-terra | 4 | 6 | no | 3046841 | 34363 | 10246 | 806997 | unavailable |

## gpt-5.6-terra

- `explicit-runtime-promotion-workflow`: 1/3 PASS, stable `false`
- `load-skill-creator-first`: 3/3 PASS, stable `false`
- Explanation complete ratio: `1.0`
- Explanation coherent ratio: `1.0`
- Base-rate API reference: `1.9670435`
- Long context indeterminate observations: `6`
