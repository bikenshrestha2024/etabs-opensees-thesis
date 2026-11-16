# 2026-11-16 22:48 GUI polling failure — evidence and correction

## Confirmed exception

User-supplied conversion progress log recorded a repeated exception from the parent Tk polling callback:

```
[WORKER POLLING ERROR] TypeError("'str' object is not callable")
... SyntaxWarning: 'str' object is not callable; perhaps you missed a comma?
components/ui/application.py:3338
```

The progress-status string in `App._poll_conversion_worker` placed a parenthesized conditional string immediately after a preceding f-string expression, so Python parsed it as a function call on the already created string instead of concatenation. This syntax is accepted by compilation, then fails **at runtime** on every active-worker poll. It suppresses the parent status update and the normal rescheduling of `after(400, ...)` within the healthy path. The outer polling exception handler may continue retries and generate many error lines. This **does not prove** the separate conversion worker stopped or that mesh processing is inherently expensive.

**Patch**: explicitly concatenate the conditional suffix with `+` and add a regression that compiles **and executes** that exact status expression with both short and long silent intervals, rather than relying only on compilation.

## Observed independent worker timings

The 22:48 user log shows source EDB loaded with 1101 points, 1367 frames, 725 area objects; extraction stage completed in 25.75 s. Four saved source Plotly 3D/floor-plan views each serialized quickly; combined trace preparation and writing was a few seconds, not minutes. The last visible stage around 22:48:37 was `Connected model assembly and analysis-file manifest`. The same log records a subsequent separate conversion using export folder `.../4`, beginning 22:52:03, reaching that same assembly stage. Do **not** conflate logs across different output roots or accept earlier HTML as proof of current assembly completion.

At 22:52:23 the second worker began complete-model assembly; `extract_source_metadata` finished about 3.7 s later. The supplied log excerpt ends before an `assembly_report` or `[WORKER_RESULT]` for this invocation. The precise duration of `prepare_complete_export` and any unhandled native assembly error cannot be established from the supplied lines.

## Performance and physics separation

- The user screenshot of `OpenSees_Load_Assignment_3D.html` shows many Plotly legend entries / load traces, which makes interactive browser use cumbersome. This is a separate **viewer UX concern** from the source ETABS export wall-clock runtime. Recorded viewer preparation timings do not support attributing the 19-minute import to HTML generation.
- `floor_subdivisions=4` controls **real** conforming shell element discretization, not the HTML mesh appearance. No support, stiffness, self-weight, or gravity analysis setting was modified in this patch.
- A second `MESH_04` build stages a separate complete assembly and workbook generation. Avoid running that during the source conversion, as concurrency adds disk/CPU work and may use incomplete inputs.
- The optional full-table LFS pointer is still unverified and its workbook is not needed to complete the ETABS-only source extract. Retain its `GIT_LFS_POINTER_ONLY` flag separately from native model status.

## Acceptance gates

1. CI: execute `python -m unittest tests.test_conversion_progress_status_runtime -v`. Verify both short and long worker silence return readable strings without TypeError.
2. Native Windows: run the same source EDB SHA with a fresh folder; confirm progress stage updates and no `[WORKER POLLING ERROR]` lines.
3. Native engineering: require current-run `[ASSEMBLY TIMING] prepare_complete_export`, `[WORKER_RESULT]`, and a non-stale `OpenSees_Complete_Export_Report_V118.json` before indicating completed import. Any reported `assembly_errors` must fail the completion gate.
4. Compare five-minute baseline against timed source extraction, visualization and complete-model assembly separately. Do not claim speed restored without native measurement.

This is a GUI-status correctness fix and regression test; it is **not** an ETABS/OpenSees gravity equivalence approval.
