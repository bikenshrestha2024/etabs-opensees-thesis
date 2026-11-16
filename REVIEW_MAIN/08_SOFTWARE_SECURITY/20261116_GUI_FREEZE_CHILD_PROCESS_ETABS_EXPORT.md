# 2026-11-16 — ETABS export GUI not responding; child-process isolation

**Status:** GUI event-loop risk corrected in source; native Windows ETABS rerun still required. No structural model, solver formulation or source EDB was changed. Separate 3D OpenSeesStudio fork was left unchanged.

## User evidence

The private uploaded timing records showed:
- Source-metadata stage from 2026-11-16 13:17:12 to 13:17:22 (+05:45), 10.220339 seconds, completed.
- Source-metadata stage from 2026-11-16 13:34:20 to 13:34:27 (+05:45), 6.725116 seconds, completed, 2,443,975-byte metadata output.

The timing index contained no failed ETABS metadata record and **no downstream detailed conversion trace**. A metadata completion does not establish full conversion or solver success. The originally blocked stage cannot be identified without the application's last lines of `ETABS_OpenSees_Conversion_Log.txt` and/or a new worker log.

## Confirmed source issue

In `components/ui/application.py`, `App._run` was a Tkinter button command executing optional workbook audit, `convert_model` (ETABS COM + assembly), visualization and export mirror **synchronously on the GUI event loop**. On a slow ETABS API call, main window repaint/input events were blocked and Windows could display **Not Responding** even though computation might continue.

## Targeted code change

- `tools/etabs_conversion_worker.py` runs original `convert_model` in a dedicated Python subprocess, including existing source-layout and optional workbook audits.
- `App._run` now launches the worker with `subprocess.Popen` and returns to Tk immediately; ETABS COM stays in the child main thread (not a new Python thread).
- Stdout/stderr are redirected into private case output at `09_SOFTWARE_DIAGNOSTICS/ETABS_Conversion_Worker.log`; GUI polls with `root.after` and displays elapsed time and seconds since last emitted log.
- GUI includes `Cancel active ETABS conversion`. Cancellation only terminates the worker process; it may leave an ETABS process running. Partial output remains unverified. **Never save the original EDB from a failed or cancelled run.**
- Worker distinguishes `EXPORT_COMPLETED_REVIEW_REQUIRED` from native ETABS/OpenSees engineering acceptance; source audit and calculated section/mesh formulations have not been altered.
- CI test `tests/test_etabs_conversion_gui_isolation.py` checks that button callback launches Popen rather than direct conversion and that the worker source exists; CI cannot exercise proprietary native ETABS COM.

## Windows check

1. Save your source EDB safely and close any stuck old GUI/ETABS sessions after checking whether they are in use; **do not force-save changed EDB**.
2. In your cloned thesis repository, `git pull origin main` and `conda activate etabs_env312`.
3. Launch `python 01_MAIN_GUI.py` using the environment containing ETABS API dependencies.
4. Select EDB and a private output folder and press **RUN ETABS → OPENSEESPY EXPORT**. Observe the progress indicator and scrolling log.
5. If the worker stays quiet, inspect `09_SOFTWARE_DIAGNOSTICS/ETABS_Conversion_Worker.log`. Note the last `[STEP START]` without a corresponding `[STEP OK]`; a silent stage is not automatically a deadlock.
6. If the export is cancelled or fails, classify it `TRUNCATED/FAILED` and do not treat the existence of source-metadata output as success.
7. On completion, inspect `OpenSees_Complete_Export_Report_V118.json`, corresponding converted model files and independent 32-support acceptance cases.

## Outstanding concerns

- This change fixes the Tkinter event-loop blocking *mechanism*, not a proven underlying native ETABS COM stall.
- Check whether `OPENSEES_PROJECT_FOLDER` and the output folder point to a very large directory; mirror and metadata operations may be expensive. Verify with stage log first.
- The renderer in `OpenSeesStudio` is an independent PySide6 app and was **not** imported into the thesis project. Its internal units are kN–mm–tonne; your thesis system uses kN–m–s. Any future display adapter must handle units and source identity explicitly.
- A separate Windows machine is required to run ETABS COM and validate source file hashes/metadata and the worker process lifecycle.

**Engineering gate:** Still `ETABS_OPENSEES_EQUIVALENCE = NOT_VERIFIED`; NLTHA X-wall first-step status unchanged.
