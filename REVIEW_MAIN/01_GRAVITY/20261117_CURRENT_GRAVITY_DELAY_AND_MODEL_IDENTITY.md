# Gravity postprocessing delay and current-model evidence boundaries

## Runtime finding

A supplied completed gravity action log spans 32 minutes 33 seconds. The native
solver subprocess returned 58 seconds after the GUI start; its gravity report
records 53.787 seconds. The dominant uninstrumented gap is 31 minutes 25 seconds
between solver-log delivery and the first source-audit completion message,
96.52% of observed wall time. Another four seconds precede source-component
messages and six seconds precede final evidence/completion messages.

This is post-solver reporting/audit latency, not evidence of a 32-minute native
solve or shell-mesh construction. Model construction is separately reported as
2.684 seconds; timing scopes may overlap, so do not blindly sum these figures.
Raw logs, source paths, project spreadsheets and pointwise reactions remain
private. No native Windows rerun was performed for this investigation.

## Inspected execution path and reproduced cause

`components/gravity/gui_and_reports.py::_worker` schedules `_finished` on Tk.
`_finished` logs solver delivery, then synchronously calls `_make_outputs`.
That function renders figures, embeds Tk canvases, creates result worksheets,
recovers floor/joint balances, calls `add_formula_audit`, and saves the workbook.
Only afterward does `_finished` run `source_load_audit`, including joint-overlap
and quantity evidence. The action log cannot split the long gap between these
operations. The existing `Gravity figure and workbook export` record in
`00_PROCESSING_METADATA/OUTPUT_TIMING_INDEX_V130.json` can narrow the interval;
its contents were not included in the supplied action log.

The older formula exporter (`8b318ec7`) calls `Worksheet.max_row` before every
loaded-node append. openpyxl scans existing cells to calculate that property,
so repeated calls on a growing sheet cause quadratic work. The branch's local
row counter removes these scans while preserving Excel paging and evidence.
A fresh Linux benchmark of the actual old and corrected functions reproduced:

| Synthetic floor cells | Loaded-node rows | Older exporter | Corrected exporter |
|---:|---:|---:|---:|
| 250 | 1,000 | 0.205 s | 0.043 s |
| 500 | 2,000 | 0.684 s | 0.109 s |
| 1,000 | 4,000 | 2.625 s | 0.209 s |

Single trials exclude XLSX save, plots and native solution. The approximately
12.6-fold improvement at 4,000 rows is not a Windows full-model timing claim.
The supplied log does not fingerprint the loaded exporter, so this reproduced
hotspot is a strong explanation rather than proof of its exact time share.
No CPU, memory, antivirus or disk measurements were supplied.

The gravity `_finished` workflow still performs reporting on Tk's event thread
and clears its busy flag before report completion. This is separate from the
slab-study root/recovery worker fix in this branch. Moving the gravity workflow
requires separating file/data operations from main-thread Tk rendering and
retaining busy state through completion; this report does not implement that
additional change or claim the remaining gravity GUI blocking is fixed.

## Model identity correction: latest photos govern

The user clarified that earlier ETABS photos were a different model. Earlier
bulk-dialog assumptions about 1 m cookie-cut floors, 5x5 walls and propagated
wall restraints are historical and must not be assigned to the current model.
The latest right-click object information shows, for the pictured objects only:

- Slab: no auto meshing, automatic edge constraints enabled, rigid diaphragm
  assignment, top cardinal point, no object-level property modifiers.
- Beam: no auto meshing, program-determined inclusion in analysis mesh,
  automatic end offsets, top-center insertion, no end releases.
- Column: no auto meshing, automatic end offsets, centroid insertion; a
  design reinforcement ratio does not supply a complete fiber section.
- Wall: default/no meshing, **Add Restraints No**, automatic edge constraints
  enabled, middle cardinal point, no object-level property modifiers.

These four objects are not a full model inventory or proof of solved EDB hash.
Object modifiers being absent does not prove section-level modifiers are unity.
Do not enable wall-edge support propagation from earlier unrelated dialogs.

Earlier private coordinate crosswalks, mesh counts and pointwise discrepancy
percentages are provisional until their source-model identity matches this
run. Matching labels/IDs or total gravity reaction alone is insufficient.
The current log confirms a converged 32-reaction-bearing-support diagnostic;
zero reaction at another source point does not prove it should be unrestrained.
Its completion message explicitly does not certify ETABS equivalence.

CSI describes intermediate-joint edge compatibility and corner load transfer,
including effects on local frame response along collinear shell edges:
[Auto Edge Constraints](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Auto_Edge_Constraints.htm).
Source-equivalent mesh/constraints, supports, section modifiers and offsets must
be established against the current model before assigning a reaction mismatch
to mesh refinement. Preserve loads and support provenance during that comparison.

## Next measurement and limitations

Restart the intended patched Python environment and record actual imported
module paths, interpreter and module hashes. Updating a checkout does not
replace already imported modules or a separate exported runtime snapshot.
Add separate phase measurements for formula creation, workbook save, plotting,
source audit and packaging before attributing the whole gap to one function.
Recover reports from a matching solved result when possible instead of rerunning
the native solve. Preserve result/source hashes and original failed states.
The nonlinear brace design remains proposed and unqualified; none of these
performance changes establishes nonlinear project calibration or equivalence.

## Integration verification

Before integration, unittest discovery passed 411 tests. The active `tests/`
pytest suite passed 454 tests and 229 subtests after selecting a temporary
location outside the host's synthetic Git markers. Initial default-temp tests
misclassified archive fixtures because the host supplies `/tmp/.git`; an
attempted alternate directory was read-only. No production change was made to
hide those environment effects. Repository-root pytest collection also enters
historical native verification scripts requiring unavailable model exports and
a display; the active suite is `tests/`. Native Windows checks remain pending.
