# P0 — Git LFS workbook incorrectly blocks ETABS model conversion

Status: OPEN_HIGH (reported 2026-11-11; reproduction on Windows pending).

## Observed
The main GUI opens a "Select original ETABS workbook" dialog saying an exported archive contains a Git LFS pointer and requests the original `etabs_full_table` workbook. This occurs before the user can complete ETABS-to-OpenSees export. Source model and output root are already selected in the main GUI.

## Engineering judgment
The native EDB selected in the application must be the sole authoritative physical model source. A full-table workbook is *optional native comparison evidence* for the Gravity/ETABS assignment audit; it must not block the primary ETABS OAPI export if the EDB is readable. Conversely, a missing source table must block only claims requiring that table. A Git LFS pointer is NOT an Excel workbook.

## Corrective implementation acceptance
- Determine the selected source EDB from the top-level GUI once; preserve its absolute path, real SHA256, model state and export source metadata. Never infer source EDB from arbitrary workbook names.
- Run core geometry, connectivity, sections, loads, mass, diaphragm and support export directly from source EDB/OAPI, read-only. If the EDB cannot be opened, fail that operation explicitly.
- Make full-table workbook validation a separate, optional `Gravity > Verify ETABS assignment tables` path; display `EVIDENCE_MISSING` if unavailable.
- Detect LFS pointer by `version https://git-lfs.github.com/spec/v1`. Do not try to parse it with openpyxl, and do not ask for it during conversion.
- Do not automatically accept a workbook from another EDB just because values look similar. Require original model identity/hash and compatible limit state.
- Save separate audit statuses: `CONVERSION_SUCCESS` versus `GRAVITY_NATIVE_TABLE_UNAVAILABLE`. Test no-workbook export and corrupted-pointer detection.
- Never upload original EDB or private workbook to this public repository.

No production conversion code was changed by this issue report.
