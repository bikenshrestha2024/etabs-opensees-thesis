# 2026-11-06 — Codex workbook shifted-layout reconciliation

## Actual source evidence supplied

Codex's text report (not the modified source files) says that an ETABS-integrated NBC 105 workbook uses a two-row-shifted `SCALING SUMMARY` layout. It reported:
- `Source EDB` label in a moved row (for example B5 instead of B4).
- X/Y wall index areas about `1.9583` and `2.2031` m² and workbook NBC adopted period references about `2.03857` and `1.92198` s, respectively, on the *historical source EDB*.
- The current ETABS-to-OpenSees export identifies a `Copy` EDB whose SHA256 did **not** match the workbook's original EDB.
- An empty or malformed `.xlsx` candidate previously caused `BadZipFile`; this was already fixed in PR #24 and remains in place.

These figures have NOT been imported into the current `Copy` model as approved inputs. Matching names, workbook selection, or a two-row layout shift does not prove physical EDB equivalence.

## New source-reader behavior

1. `components/inputs/project_workbooks.py::_scaling_summary(ws)` searches bounded workbook rows for a `Source EDB` / `ETABS model` label and candidate `.EDB` path rather than relying exclusively on B4. It identifies X/Y rows with explicit axis labels, validates numeric Aw and adopted-period cells, and returns their **real cell coordinates**. B14/C14 and B15/C15 remain supported when both cells actually contain valid positive numeric values.
2. The source `SCALING SUMMARY` is eligible only through `source_workbooks()`, which checks Ultimate→ULS or Service→SLS, floor and source EDB identity. Distinct EDB bytes remain unverified. A workbook selected only as a calculator may NOT bypass this check through a scaling tab.
3. `components/inputs/etabs_periods.py` reads the same labelled row coordinates and keeps workbook adopted periods **separate** from ETABS-measured eigenperiods. Workbook adopted periods cannot fill the live/ETABS reference period field on their own.
4. Invalid/empty XLSX files remain individually skipped by the existing BadZipFile handling; original workbook and EDB bytes are read-only.

## What is required before filling the latest model's Aw

On the Windows source machine, run the selected Ultimate/ULS ESM export. Check `OpenSees_Element_Connectivity.json` for the actual `source_edb`, then open the scaling workbook and review the `Source EDB` row. The historical `1.9583 / 2.2031` values and `2.03857 / 1.92198` adopted T references remain **unqualified** until the source EDB bytes or independent geometry/material equivalence can be verified. Use the OpenSees wall pier audit as a separate diagnostic and retain first-storey opening/pier grouping reviews.

Test on Windows with:

```powershell
git pull --ff-only origin main
python tests/verify_esm_aw_period_provenance.py
python tests/verify_nbc105_periods.py
```

Open the ESM dialog, select the actual source export, and use `Excel sources…` or `Why are Aw/period fields blank?` to see the matching-source status. A blank field for a genuinely different EDB is **correct fail-closed behavior**, not an invitation to bypass the validation.

**Test coverage:** synthetic shifted labelled rows, original vs Copy mismatch, calculator-tab bypass, existing old-layout tests and previously fixed invalid XLSX regression. No native ETABS/physical-wall validation occurred in GitHub CI; no source project files were modified.
