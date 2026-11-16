# 2026-11-16 — Source viewer optimization and complete model assembly profiling

## Engineering status

**READ-ONLY VISUALIZATION / ASSEMBLY DIAGNOSTICS**. Not an ETABS/OpenSees structural equivalence pass. No changes to floor_subdivisions, actual ShellMITC4 mesh, 32/76/97 support sets, source joints, gravity mass or model stiffness.

## User evidence

November 16 parent log (root .../3) shows:
- ETABS source extraction 25.75 seconds for 1101 original points, 1367 frames, 725 areas, 25 stories.
- Four source 3D/plan views complete within ~3.74 seconds. 2092 connectivity source elements and ~2850 individual 3D load triangles/line traces shown.
- Connected model assembly starts ~22:48:37; ETABS source metadata extraction ~3.83 seconds; rest of original worker run incomplete in supplied log.
- New conversion to separate folder .../4 started around 22:52; it reached connected model assembly and source metadata extraction ~3.68 seconds. No final successful report was supplied.
- Parent GUI repeatedly throws `TypeError("'str' object is not callable")` during status polling in that older Windows process. That bug was fixed separately in main commit 01c95361; a running old Python process will not reload the fix.

The graph is a **browser rendering issue**, rather than a demonstrated 15-minute export workload. Actual assembly-phase timing remains unknown.

## Visualization-only changes

- Keep exact source connectivity records, ETABS IDs, OpenSees element mapping and specialized element-classification taxonomy. Compress 3D connectivity into batches grouped by story/category/property, plus one selected-element overlay. Filtering still exposes all individual source objects.
- Compact 3D surface loads using indexed Mesh3d triangles and group frame arrows; preserve source object hover data and per-pattern/UDL-value filtering.
- Log original versus batched trace counts. Preserve the original CSV/JSON load audit and source mapping. Rendered triangles still represent the same load visualizations and do not act as engineering force transfer.
- The floor-plan viewer remains separate and editable: do not substitute screenshot geometry for native ETABS assignments.

## Assembly-stage forensic logging (not load-path modification)

Instrument existing `components/model/assembly.py::prepare_complete_export` and `_mesh_areas`:
1. conforming shell mesh: heartbeat every 75 area panels; cells and elapsed wall time
2. frame-node spatial index: total bins, elapsed
3. frame-member splitting: heartbeat every 250 source frames, generated segments
4. member offset/weight/joint-volume and load-ledger stage: elapsed
5. independent load-path audit: elapsed

This exposes which assembly phase takes minutes without shortening mesh or altering numerical relationships. The timing output is on the child worker stdout / log. Compare separate stages with yesterday's known five-minute baseline under the same EDB SHA, same 4x4 config, fresh output directory and same options. If there is no `[ASSEMBLY PHASE OK]` after a `START`, isolate that phase before changing its algorithm.

## Validation gates

- `tests/test_source_view_compaction.py` checks that geometry, source IDs, sections, member load hover records and mesh triangle connectivity survive batching.
- Repository CI, source guides and security checks must pass before merging.
- Native Windows ETABS COM, browser rendering latency and full assembled shell gravities are not exercised by Linux CI. Retest on the source machine and confirm a fresh `OpenSees_Complete_Export_Report_V118.json`, `[WORKER_RESULT]` and no engineering assembly errors.
- Benchmark saved view open time and frame rate separately; no unmeasured 5-minute performance claim.

**Privacy:** Never commit local EDB or the original workbooks to the public repository.
