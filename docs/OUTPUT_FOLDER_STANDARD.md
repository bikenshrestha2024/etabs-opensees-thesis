# Uniform output-folder standard

[REF docs/source/components/inputs/output_contract.py.md]

Every new analysis run writes to one identified directory. The layout is created by `components.inputs.output_contract.create_case_run`; this page documents it. Check a run with `python tools/audit_output_layout.py RUN_DIR [--json]` (read-only, exit 0 when the layout conforms, 1 otherwise).

## Run tree

```
<export>/<stage folder>/RUNS/<state>/<case>/<UTC stamp>_<hash>/
    00_INPUT_SOURCE/    inputs, config, scripts used; CASE_MANIFEST.json
    01_LOGS/            run and solver logs
    02_RESULTS/         JSON and CSV results
    03_EXCEL/           workbooks
    04_FIGURES/         figures
    05_COMPARISONS/     comparisons (for example ETABS vs OpenSees)
    06_REVIEW/          review and acceptance notes
    07_EXPORT_ZIP/      zip archive of the run
```

The run id is `YYYYmmddTHHMMSS_ffffffZ_<8 hex>` (UTC stamp plus a random hash); a new directory is created on every call and an existing one is never reused. `<stage folder>`, `<state>` and `<case>` are single Windows-portable path segments validated by `output_layout.canonical_stage_folder` and `output_contract.safe_component`. Nothing else may sit directly in the run directory, and no entry may be a symbolic link.

## Status vocabulary

`CASE_MANIFEST.json` (schema `ETABS_OPENSEES_OUTPUT_CASE_V1`) records `solver_status`, one of `output_contract.STATUSES`:
`CREATED`, `RUNNING`, `COMPLETED_SOLVER_ONLY`, `FAILED`, `INTERRUPTED`, `INCOMPLETE`, `VERIFIED_ETABS_EQUIVALENCE`.
`structural_acceptance` is `NOT_VERIFIED` until a human engineering review sets `VERIFIED_BY_ENGINEERING_REVIEW`. A solver status, and a layout audit PASS (`LAYOUT_ONLY_NOT_ENGINEERING_ACCEPTANCE`), are never engineering acceptance. `VERIFIED_ETABS_EQUIVALENCE` in a manifest is itself reported as `MANUAL_ENGINEERING_CERTIFICATION_REQUIRED`.

## Where else things go

- Findings derived from a run: `docs/validation/run_findings/<STAGE>_<RUNID>.md` and `.json` (repository side; the run folder keeps the raw outputs).
- Agent edit evidence: `engineering/agent_edits/` (model label UNKNOWN when not available).

## Producer status

The subfolder roles in the run tree are the target convention, and the audit checks only the top-level layout and the manifest, not which files sit in which subfolder.

Only the four modules below were identified as writing ad hoc folders (they call `mkdir` on a caller-supplied output path and do not use `create_case_run`). They are listed here and are **not migrated** by this change. This is not an exhaustive audit of all producers: other modules import `output_contract` and are not listed.

| Module | Output layout |
|---|---|
| `components/nonlinear_time_history/building_exploratory.py` | ad hoc (`output_dir`, per-orientation folders) |
| `components/nonlinear_time_history/literature_demo.py` | ad hoc |
| `components/nonlinear_time_history/full_record_gate.py` | ad hoc |
| `components/nonlinear_time_history/energy_balance.py` | ad hoc |

Two further LTHA runner behaviours the audit cannot detect (verified in `components/linear_time_history/runner_and_gui.py`): outside contract mode it writes an ad hoc `LTH_<limit state>_<scope>_<stamp>` folder under the chosen output directory; in contract mode it writes its `.xlsx` and `.png` files into `02_RESULTS`, and only for a run whose completion gate passes does it copy `.xlsx`, `.png` and `.pdf` files of 25 MB or less into `03_EXCEL` / `04_FIGURES`.

Old outputs stay where they are; the audit tool reports them as non-conforming rather than moving them.
