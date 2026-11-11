# P1 — NLTHA earthquake record duration display

Status: GUI PREVIEW IMPLEMENTED, Windows native execution not yet verified.

## Change
`components/nonlinear_time_history/runner_and_gui.py` adds an `Inspect exact selected X/Y record durations (read-only)` button. It uses the existing shared `_read_inputs` parser with selected pair manifest, record paths and story-master CSV; it does not launch an analysis or bypass readiness.

Each component is separately labeled with sample count `NPTS`, native time step `DT`, and duration `(NPTS-1)*DT`; the XY/YX planned interval and short diagnostic versus full-record interval are presented. Mismatched component intervals are flagged for review instead of silently trimming/padding.

## Review requirements
- Use real PEER/SeismoMatch files in Windows to validate X/Y and swapped orientation, including Gorkha 322.94 s versus purported original 120 s and the Loma Prieta one-sample issue.
- Distinguish source sampling interval, physical record duration, solver integration dt, diagnostic requested duration, and successfully integrated end time.
- A selected record does not imply a completed full-record, accepted, or calibrated nonlinear response.
- Verify the button does not run when record inputs are invalid and the exception is shown with complete filename.

No full native solver verification is claimed.
