# V18 output evidence integrity review — 2026-11-15

**Status:** SOURCE_CORRECTIONS_COMMITTED; TEST EXECUTION AND NATIVE WINDOWS CHECKS PENDING.
**Branch:** `main`. **Scope:** actual contents of `components/inputs/output_contract.py`, `components/inputs/output_layout.py`, `components/inputs/project_output_layout.py`, `tools/audit_stage_output_migration.py`, `tests/test_unified_output_contract.py`, `AGENTS.md` and existing V16/V17 review. This is a targeted semantic inspection, **not** an every-line review of the full repository.

## Defects newly confirmed and corrected

### V18-01 — nonfinite CSV values could be published as valid numerical results

The shared `write_table()` claimed it used finite values but did not check them. `csv.DictWriter` would write `nan`, `inf`, or `-inf` for floating nonfinite inputs. These cannot be treated as valid gravity reactions, modal periods, base shears, drifts or time-history results.

**Correction:** Reject nonfinite real floating scalars (including NumPy float32/float64 when available) and Decimal values before `writer.writerow()`. Existing write uses a temporary file and atomic replacement, so exceptions remove its temporary output and leave the previous output untouched. Also reject empty/whitespace/non-string CSV headers. All finite values and standard CSV formatting remain unchanged.

**Regression added:** `test_csv_rejects_nonfinite_numeric_values_without_publishing`, `test_csv_rejects_numpy_nonfinite_scalars_when_available` and `test_csv_rejects_empty_and_nonstring_headers` in `tests/test_unified_output_contract.py`.

**Explicit limitation:** String `"NaN"` values and third-party non-Real numerical wrappers require validation upstream; this is a central output guard, not complete engineering validation of every source. Other CSV/Excel writer functions not using `write_table()` remain outside this patch.

### V18-02 — a valid-looking case manifest could be recorded under the wrong stage

`inspect_case_manifest(run_dir)` previously compared the manifest's `stage` against the caller's `expected_stage` **only if passed**, even though the directory path already encoded the owning stage. A copied/falsified `03_ESM` manifest in `05_MRSM` could therefore be treated as structurally valid by a caller omitting that argument.

**Correction:** Validate the declared stage through the canonical stage registry and require exact agreement with the containing stage folder in `<stage>/RUNS/<state>/<case>/<run-id>`. Unknown or alias-only stages are flagged. Existing optional `expected_stage` still adds a second explicit constraint.

**Regression added:** `test_manifest_stage_identity_validated_without_expected_stage` checks a genuine gravity manifest followed by wrong, unknown and noncanonical stage identities.

**Explicit limitation:** Valid structural metadata is not proof of solver convergence, model SHA equivalence, correct stiffness/mass, support reactions, NBC 105 compliance or complete NLTHA.

## Standard outputs and review ownership

The established target root is the **selected ETABS export case**, not the checkout root and not a freshly invented output directory:

```text
<SELECTED_ETABS_EXPORT_CASE>/
  00_SOURCE_MANIFEST/
  01_ETABS_EXPORT/{00_MANIFEST,01_SOURCE,02_MAPPING,03_LOADS,04_VISUALIZATION,05_AUDITS,06_CONFIG,07_LOGS,08_PROCESSING,09_REVIEW}/
  02_MODEL/
  02_GRAVITY/RUNS/<STATE>/<CASE>/<RUN_ID>/
  03_ESM/RUNS/<STATE>/<CASE>/<RUN_ID>/
  04_MODAL/RUNS/<STATE>/<CASE>/<RUN_ID>/
  05_MRSM/RUNS/<STATE>/<CASE>/<RUN_ID>/
  06_LINEAR_TIME_HISTORY/RUNS/<STATE>/<CASE>/<RUN_ID>/
  07_NONLINEAR_TIME_HISTORY/RUNS/<STATE>/<CASE>/<RUN_ID>/
  08_ETABS_COMPARISONS/
  09_SOFTWARE_DIAGNOSTICS/{DISK_AUDITS,MIGRATION_AUDITS,WRITER_AUDITS}/
  90_UPLOAD_PACKAGES/
  REVIEW_MAIN/
  OpenSees_Analysis_Results/  # historical, unchanged
```

Each `create_case_run` output has `00_INPUT_SOURCE`, `01_LOGS`, `02_RESULTS`, `03_EXCEL`, `04_FIGURES`, `05_COMPARISONS`, `06_REVIEW`, `07_EXPORT_ZIP`. Legacy producers/consumers need migration one stage at a time; directory existence does not mean all stage writers use it.

## Additional inspected issues — unresolved, not silently fixed

1. `atomic_json` and `write_table` are generic file writers accepting arbitrary caller-provided destinations. They must not be regarded as a universal path-junction or permissions sandbox. The writer/reader migration inventory and Windows adversarial path tests remain necessary.
2. `create_project_layout` and `case_folder` implement another output API besides `create_case_run`; these two layouts have different case-nesting semantics. Do not unify by moving existing results without testing all GUI callsites and historical readers.
3. `audit_stage_output_migration` counts only already-created central contract manifests. A stage with zero manifests is **not evidence that no solver result exists**: it may use a legacy writer.
4. `inspect_case_manifest` is a filesystem/metadata acceptance check only; source file hashes, signed gravity/seismic forces, numerical convergence and complete records must be validated by separate native checks.
5. An existing `REVIEW_MAIN`, `07_REVIEW_MAIN`, `docs/review` and stage-local reviews should be preserved. The canonical case-local engineering review and repository-wide review index need explicit cross-linking rather than automatic folder moves.
6. The native nonlinear X-wall first-step nonfinite force, actual project rebar/wall elements, 32/76/97 foundation support basis, source workbook Aw and adopted period values, ULS/SLS modal/MRSM and XY/YX full records remain **NOT_VERIFIED**.

## Run and acceptance checklist

```powershell
python -m unittest tests.test_unified_output_contract -v
python -m unittest tests.test_deep_output_inventory_v16 tests.test_folder_audit tests.test_output_layout tests.test_stage_output_migration_audit -v
python tools/audit_live_output_writers.py --repo .
python tools/audit_stage_output_migration.py "<PRIVATE_SELECTED_EXPORT_CASE>" --write
```

Keep the generated report under the selected export case's `09_SOFTWARE_DIAGNOSTICS`, not the public GitHub tree. On Windows, verify a finite gravity/ESM/MRSM history CSV still writes normally; a NaN does not publish; and manifest stage mismatch appears as invalid. Additional validation must include ETABS vs OpenSees numerical comparisons using the user's private source model and original Excel calculations.

**No native solver testing was executed in this review. No original EDB/XLSX was changed. No claim of entire-repository line-by-line audit is made.**

## CI feedback and repair

At commit `1e22c4a77047333d10263fc1590d69a7cbe68590`, GitHub Actions [NLTHA Python quality checks](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/43664867271) failed at `test_csv_rejects_nonfinite_numeric_values_without_publishing`: an incorrect test literal compared a CSV with actual newlines against a Python string containing escaped backslash-n characters. The test assertion was corrected in commit `f43c19520b936771f47fe52ad20ebab7a59f21d5`. Syntax and other focused tests in the log were passing up to that test. This was **a test expectation defect**, not evidence of a solver discrepancy. Later CI conclusions should be recorded separately after completion; no native ETABS, Windows or OpenSees run is established by this GitHub check.
