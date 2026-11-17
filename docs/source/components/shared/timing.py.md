# timing.py — source documentation

**Python source:** [components/shared/timing.py](../../../../components/shared/timing.py)
**Git baseline content SHA:** 5e321558283f2ff86caa37f97c841519a069db84
**Subsystem:** Solver, logging and response numerical utilities
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the shared implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: See subject-specific source citations. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-15 — canonical processing metadata (new runs only)

The old `timed_outputs` and `StageTimer` created `<artifact>.processing.json` beside every CSV/JSON/XLSX/PY result, proliferating hundreds of incidental root-level JSON files and cluttering user result folders. **New runs** retain original artifacts at their existing source paths for reader compatibility, but keep timing sidecars in `<selected-stage>/00_PROCESSING_METADATA/ARTIFACTS/<relative-subfolder>/<artifact>.processing.json`, with a single index and JSONL log inside `00_PROCESSING_METADATA/`. This is non-destructive: historical sidecars, original ETABS EDB/Excel, and solver outputs are never moved/deleted. Timing evidence cannot be mistaken for numerical analysis results. Nested metadata is filtered out on subsequent scans to prevent recursive sidecar generation.

This is a **specific writer correction**, not full migration of all legacy export-root sources. Complete root cleanup needs source reader migration, verified SHA manifests, rollback and native regression evidence. Source-only independent tests: `tests/test_timing_metadata_structure.py`; native dependent legacy tests adjusted: `tests/verify_v130.py`.

For explicit stages, `StageTimer` snapshots the size and modification time of immediate output files at startup. On finish it records newly created and observably modified files. Elapsed time uses a monotonic clock, and output selection works across wall-clock adjustments. Same-size rewrites with identical filesystem modification timestamps are indistinguishable from untouched files.


## 2026-11-17 short-run failure evidence correction

Prior timed_outputs used nanosecond wall clock and per-file mtime comparisons. Coarse filesystem timestamps could omit a new artifact and its failure-status sidecar. The wrapper now snapshots eligible files before and after each stage and records newly created or changed artifacts, excluding prior unchanged outputs. Failure exceptions propagate and processing sidecars live in 00_PROCESSING_METADATA/ARTIFACTS. Deterministic skew and existing stage tests: tests/test_timing_metadata_structure.py. This is timing metadata integrity, not native solver or engineering acceptance.
