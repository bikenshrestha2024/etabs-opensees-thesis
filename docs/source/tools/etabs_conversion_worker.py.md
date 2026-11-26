# tools/etabs_conversion_worker.py

**Responsibility:** spawn-safe, independent ETABS source-to-OpenSees conversion process invoked by `components.ui.application.App._run`; original `convert_model` is reused without changing numerical/geometry assignments.

The worker receives `--edb`, `--output`, optional `--include-live` and `--categorize`. It creates the project output layout, checks optional gravity workbooks without blocking EDB extraction, runs existing `convert_model` on the same worker main thread that owns ETABS COM, verifies that the expected `OpenSees_Complete_Export_Report_V118.json` exists, and optionally produces organized export mirrors.

**Streams:** emits timestamped stage logs to stdout with `flush=True`. GUI redirects stdout and stderr to `<case>/09_SOFTWARE_DIAGNOSTICS/ETABS_Conversion_Worker.log` and polls. A final `[WORKER_RESULT]` JSON record means the worker finished; `EXPORT_COMPLETED_REVIEW_REQUIRED` is NOT a model acceptance status. Failure emits traceback and a nonzero exit code; GUI must reject partially written data.

Before overwriting export files, the worker writes `00_SOURCE_MANIFEST/IMPORT_INCOMPLETE.json` in the selected case. It removes the marker once a fresh assembly report passes the worker completion checks. Failure or cancellation before that point leaves the marker in place. Workbench actions that resolve a folder through Model review block that case until a successful Import. Older exports without a marker and independent rebuild folders remain available.

Before ETABS opens its private working copy, the converter checks the copy's SHA256 against the EDB digest already recorded in the project context. This catches an EDB replacement between source registration and COM startup, even when the replacement has the same file size.

**Constraints:** do not add any Tk calls or model-state mutation beyond the existing conversion pipeline. Never open source EDB in write mode or change its hash. COM process must not be moved to an ordinary Python thread. No source/derived model files may be committed publicly. Cancel terminates the worker process; separately spawned ETABS processes may remain and must be inspected by the operator.

**Testing:** `tests/test_etabs_conversion_gui_isolation.py` and `.github/workflows/etabs-conversion-gui-isolation.yml` are non-native source-level tests. A Windows run with native ETABS installed is required to validate the COM/ETABS worker lifecycle and no-save source policy. [Freeze investigation](../../../REVIEW_MAIN/08_SOFTWARE_SECURITY/20261116_GUI_FREEZE_CHILD_PROCESS_ETABS_EXPORT.md)
