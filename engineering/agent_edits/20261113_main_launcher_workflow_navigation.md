# 2026-11-13 main GUI workflow navigation

**Agent/model:** GPT-6 (software UI revision only; physics deliberately untouched)
**Source:** components/ui/application.py via the V116 compatibility launcher.
**Scope:** Main Tk launcher organization, callback discovery and conversion-log controls.
**Change:** Replace three long button columns with seven engineering workflow stage tabs, original source-import controls above navigation and an indexed search which invokes the preserved handler. Shorten titles for Windows DPI. Preserve all 41 existing action declarations and four saved-view entries. Compact two header utilities; add log X/Y scroll and Copy/First/Latest controls.
**Why:** The first viewport previously exposed a dense three-column list mixing source import, material calibration, nonlinear analysis and output interpretation before completing their prerequisites. Buttons for downstream methods competed with the source EDB import action.
**Physical safety:** ETABS original EDB is still read-only in the existing extractor; unchanged source model/physics, no modification to solver paths, routines, materials, seismic settings, SLS/ULS, or automatic case acceptance.
**Regression:** tests/test_main_launcher_workflow_layout.py, repository compilation and navigation CI. Native Tk responsiveness/Windows DPI, heavy ETABS COM import and actual external module callbacks remain manual checks.
**Unrelated blocked CI:** Auto LFS workbook recovery job fails in its existing project_workbooks.py registry path when a fixture simulates a Git LFS pointer in an archive without Git metadata. No LFS or workbook code changed by this UI branch. Must be investigated independently; not silently treated as pass.
**Files changed:** components/ui/application.py; tests/test_main_launcher_workflow_layout.py; .github/workflows/repository-integrity.yml; docs/source/components/ui/application.py.md; docs/source/tests/test_main_launcher_workflow_layout.py.md.
