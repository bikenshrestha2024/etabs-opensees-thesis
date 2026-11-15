# V27 — Output identity, linked writer paths and seven-gate status

Date: 2026-11-15. Git main baseline: `777a87fdcec169bfd395b14f1a859b3eeeeae807`.
Review scope: selected active source functions and their callers/tests only, **not all 2,995 tracked files**.

## Confirmed software defects

1. `components/inputs/output_contract.py::safe_component` previously converted `None`, `True`, and `False` to literal folder names. These are missing/boolean source identifiers, not trustworthy case labels. V27 now rejects them.
2. `inspect_case_manifest` previously called `safe_component` but did not require a string or exact canonical spelling. Whitespace-wrapped identifier fields could pass the component grammar check, despite disagreeing with the canonical run path. V27 now flags noncanonical or missing case/state/run IDs, while preserving existing valid identifiers and stage folder names.
3. Both `atomic_json` and `write_table` staged writes before replacing the output, but still followed symbolic links in an output destination's path chain. V27 rejects pre-existing linked destination files/directories before creating the folder, before creating temporary files, and immediately before atomic replacement. The check guards standard symbolic-link redirection, but is not a complete protection against OS-level concurrent directory swaps (TOCTOU). Existing verified native output files remain untouched.

## Regressions and CI

`tests/test_unified_output_contract.py` now tests missing/boolean case IDs, noncanonical manifest metadata, blocked symlinked output directory and destination file, and preservation of existing data. Existing syntax/CI and Windows headless output-contract workflow were invoked. The passed/reviewed GitHub Actions run should be recorded by SHA rather than inferred from a general badge; **no interactive Windows GUI, ETABS COM or native OpenSees solve was executed**.

## Stage hierarchy and reader compatibility

New adopted runs continue the established output contract:
```text
<SELECTED_ETABS_EXPORT_CASE>/
  00_SOURCE_MANIFEST/
  01_ETABS_EXPORT/
  02_MODEL/
  02_GRAVITY/
  03_ESM/
  04_MODAL/
  05_MRSM/
  06_LINEAR_TIME_HISTORY/
  07_NONLINEAR_TIME_HISTORY/
  08_ETABS_COMPARISONS/
  09_SOFTWARE_DIAGNOSTICS/
  90_UPLOAD_PACKAGES/
  REVIEW_MAIN/
  OpenSees_Analysis_Results/  # historical read compatibility
```

For each migrated stage use `RUNS/<STATE>/<CASE_ID>/<RUN_ID>/{00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP}`, with `CASE_MANIFEST.json`. This is the **target for migrated producers**, not a claim that every legacy producer already conforms. Historical source EDB/XLSX, output readers and archived results are preserved.

## Seven engineering and software requirements

| Requirement | V27 contribution | Gate |
|---|---|---|
| Full file-by-file semantic audit | Exact active-source review plus blob ledger, repository inventory only for remainder | OPEN |
| Complete writer and reader migration | Shared writer and manifest identity hardened | OPEN |
| Native Windows interactive regression | Headless Windows output test only | OPEN |
| X-wall first-step error | V26 failure evidence retained; root cause not changed | OPEN |
| Physical 32/76/97 supports | V25 source support diagnostics retained; no source restraint/mesh changes | OPEN |
| ETABS/OpenSees numerical equivalence | Prevent wrong-source manifest and CSV/JSON identity errors | OPEN |
| 224 nonlinear full-duration orientation cases | No native analyses run, numerical gate unchanged | OPEN |

Software quality checks are **not** NBC 105:2025 compliance, reinforcement/material qualification or physical ETABS–OpenSees equivalence.

## CI-discovered omission and corrective commit

The first shared-writer implementation at `89f40089caf98b215b31a3743c15e103ceef8d75` failed Linux NLTHA quality checks because the JSON writer was guarded but `write_table()` lacked the equivalent link checks. This was a real regression-test finding, not a native structural failure. Corrected in commit `1f30da26b7a9b9c97a314f2588bce8bd77514b1f`: CSV now verifies output destination path components before directory creation, after directory creation, and before atomic replacement. The Windows headless run for the corrected code passed: https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43676208534. Deep output writer inventory and repository compilation likewise passed at that code revision. The Linux NLTHA suite was still running when this record was authored; do not mark it passed until GitHub reports its conclusion.

Source review ledger was updated to blob `139674b30d7674809dae7f20c23db9448126b8cb` after the CSV correction. Tests use synthetic temporary paths, not user ETABS model exports. Atomic file replacement is not a transactional commit of entire multi-file report sets.
