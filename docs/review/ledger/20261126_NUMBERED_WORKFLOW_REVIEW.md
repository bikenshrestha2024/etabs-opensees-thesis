# Numbered workflow review, 2026-11-26

The review started at `01.py` on `0b6391fd811f33afedd5b9616cbcf0a9d1d99a88`. The numbered entry point inspection covered all 57 root Python files with two-digit prefixes, including compatibility aliases and audit utilities. The groups below refer to filenames as they exist in Git. The [program index](../../programs/00_PROGRAM_INDEX.md) identifies the canonical execution order.

| Files inspected in full | Count | Scope |
| --- | ---: | --- |
| `01.py` and the `01_*.py` launchers | 4 | Workbench startup, alias behavior and handoff to the launcher |
| `02_*.py` through `21_*.py` | 41 | Canonical stages, compatibility aliases, and model export utilities |
| `22_*.py`, `27_*.py`, `29_*.py`, `30_*.py`, and `32_*.py` through `38_*.py` | 12 | Folder audit, NBC input sync, device benchmarks, calibration, spectrum preparation, evidence and direct NLTHA |

## Corrections and evidence

- Startup aliases can be imported without opening windows. Startup and callback logs retain the original exception. The native Windows smoke check opened the workbench through `01.py`. [Launcher guide](../../programs/01_MAIN_GUI.md)
- The Import worker binds the private EDB copy to the recorded source digest. A failed in-place conversion leaves a marker for workbench actions that resolve their export through Model review. The tests exercise a same-size EDB replacement and a failed conversion followed by a successful retry. [Import worker guide](../../source/tools/etabs_conversion_worker.py.md)
- Gravity workbook staging publishes a replacement manifest only after both SHA-addressed copies verify. A regression test interrupts the second copy and checks that the previous pair remains readable. The project ULS comparison settings live in the repository's validation folder. [Workbook staging guide](../../source/components/inputs/gravity_evidence_stage.py.md) · [ULS comparison settings](../../validation/20261121_native_gravity_uls.json)
- ESM combined exports now check calculation evidence before creating a snapshot. Two exports issued at the same timestamp get separate review folders and ZIP files. [ESM export guide](../../source/components/equivalent_static/organized_exports.py.md)
- The Stage 22 mirror and audit resolve the same owning export folder when started from a known nested stage. [Folder audit guide](../../source/components/inputs/folder_audit.py.md)
- The failed-element lookup uses the solver tag's matching position in the source-object wall mesh. The triage and nonlinear performance tools check saved model, case and history evidence before interpreting the results. [Element lookup](../../programs/20_TRACE_FAILED_ELEMENT.md) · [Triage](../../programs/21_NLTHA_TRIAGE.md) · [Nonlinear performance](../../programs/18_NONLINEAR_PERFORMANCE.md)
- Report tools reject output paths that identify their inputs. The native-device CLI returns a nonzero status after a failed step and retains the failure report. Direct NLTHA redirects a selected legacy or wrong-stage folder into a source-bound run beneath `07_NONLINEAR_TIME_HISTORY/RUNS/<state>/<case>/<run-id>/02_RESULTS`. [Device benchmark](../../programs/29_NATIVE_FVD_BRB_RECORDER_VALIDATION.md) · [Direct NLTHA](../../programs/38_DIRECT_EXISTING_MODEL_NLTHA.md)
- The variant comparison file changed. Its prior exact-source attestations are preserved with their original blob digest. [Superseded attestations](superseded_semantic_review_attestations_20261126.csv)
- The literature index and inline references were reconciled for the reviewed NBC, PEER, BRB, wall, and device sources. The BRB work-equivalence reference and the implemented travel comparison are identified separately. Four broken relative links were corrected. [Literature catalog](../../../LITERATURE/README.md) · [BRB references](../../../LITERATURE/BRB/README.md)

## Coverage still open

The baseline automated scans inventoried 3,566 tracked files and syntax-checked 743 active Python files. The repository media check verified 68 local XLSX containers and 91 tracked raster images. The separate local project scan checked file integrity in the case tree, including 292 ZIP and XLSX containers. These checks cover parsing, archive integrity, and stored spreadsheet error cells. Formula recalculation, native ETABS comparison, and line-by-line review of the remaining implementation modules require their own evidence.

- The Import marker covers workbench actions that resolve the case through Model review. Direct CLI readers and already-open review windows can bypass that check. Concurrent Import workers started in separate workbenches still share the in-place output tree.
- The legacy Stage 36 matrix output needs further case-ownership review.
- The software changes preserve the 32 physical supports and 44 wall mesh points, full gravity `1.0D + 1.0L`, and the separate NBC seismic-weight basis. The published elastic reaction residual and the production NLTHA material and model review remain open. [Gravity residual audit](../../validation/20261122_REBUILT_ELASTIC_768KN_RESIDUAL_AUDIT.md) · [Project physical-model contract](../../../engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md)
