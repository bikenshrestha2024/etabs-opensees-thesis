# RTFC — Implement robust M0–M6 Soil C nonlinear comparison

## ROLE
Computational earthquake-engineering researcher implementing reproducible paired NLTHA comparisons and experimental/numerical quality gates.

## TASK
Review the current Stage 35 preflight, Stage 36 run matrix, Stage 37 JSON schema, existing nonlinear runner, full-record completion checks and `variant_comparison.py`. Improve one verified issue while preserving source hashes, wall geometry and structural-mass invariants.

## FORMAT
Provide a 00–NN ordered execution map, exact M0–M6 × eight earthquake × XY/YX × ULS/SLS case IDs, progress/failure evidence, quantitative comparisons, code diff, tests and citations. Separate worst-single-case envelope and eight-pair aggregate. Keep incomplete runs excluded.

## CONSTRAINTS
No claim of 224 completed analyses from generated config files. Do not average 16 orientations as if they were 16 independent earthquake pairs. If an eight-pair mean uses a conservative maximum XY/YX per pair, identify that separately as an engineering interpretation. No acceptance on an elastic-wall diagnostic. Use all eight same already-matched Soil C sources for each M0–M6. Distinguish ULS and SLS input basis and required review.
