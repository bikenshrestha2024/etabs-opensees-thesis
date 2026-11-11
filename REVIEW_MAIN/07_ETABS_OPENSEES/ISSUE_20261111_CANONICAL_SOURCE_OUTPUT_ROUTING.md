# P1 — One authoritative EDB and one canonical output root

Status: OPEN_HIGH. This document is an engineering work order, not an implemented router.

## User-selected inputs
The main GUI has already selected an original ETABS `.EDB` and a main output folder. Child Gravity, ESM, Modal, MRSM, LTH and NLTHA dialogs should inherit those two selections. Treat the EDB as the authoritative immutable physical model, not independently selected alternate spreadsheets or previously exported test models. It is legitimate for downstream analysis to run generated OpenSees Python files, but their manifest must trace back to the selected EDB SHA256.

## Proposed local output tree (outside public GitHub)
```
<selected_output_root>/
  00_SOURCE_MANIFEST/
  01_ETABS_EXPORT/<run-id>/
  02_GRAVITY/<ULS-or-SLS>/<run-id>/
  03_ESM/<ULS-or-SLS>/<run-id>/
  04_MODAL/<ULS-or-SLS>/<run-id>/
  05_MRSM/<ULS-or-SLS>/<run-id>/
  06_LINEAR_TH/<ULS-or-SLS>/<pair>/<XY-or-YX>/<run-id>/
  07_NONLINEAR_TH/<model-id>/<ULS-or-SLS>/<pair>/<XY-or-YX>/<run-id>/
  08_COMPARISONS/<run-id>/
  REVIEW_MAIN/<analysis>/<case-id>/00_ISSUE...09_REVIEW_SIGNOFF/
  90_UPLOAD_PACKAGES/<module>/<run-id>/
  LATEST_RUNS.json
```

## Acceptance criteria
- One immutable `ProjectContext` object holds original EDB absolute path, SHA256, limit state, source export hash, selected root, active generated model path and timestamp.
- Submodules receive explicit `ProjectContext` and may choose a different *analysis state* without silently changing the original EDB.
- Each run creates unique non-overwriting subfolders; ensure symlink/path traversal cannot put outputs outside the selected root.
- Every `run.json` records exact input/model hash, executable, Git revision, units, statuses, provenance, elapsed time, paths, and analysis acceptance categories.
- Keep existing output paths backwards-compatible until readers, source guides and regression tests are updated. Never move historical evidence.
- Latest pointers are updated atomically only after a successful complete write. Review ZIPs reference exact case hashes, and no circular re-bundling of prior ZIPs.
- Confirm no sensitive original model files, private Excel, personal paths or large native evidence are committed to GitHub.
- Preserve `00_INPUT_PROVENANCE` evidence distinctions: missing optional workbook cannot block OAPI export, but it can block ETABS-native validation claims.
