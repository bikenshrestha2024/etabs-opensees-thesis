# V126 mapping tree and 3D source preview: 2026-11-24

**Scope**: source-only Tkinter viewer correction in `components/sections/mapping_gui.py` plus synthetic tests. **Editor**: ChatGPT via connected GitHub connector. **Base** `main=4914cbd5810fa46cb46417db12071d459417ee97`, **PR #193**.

## Read-first and source evidence

Read `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, `docs/source/components/sections/mapping_gui.py.md`, `mapping_audit.py.md`, current `components/sections/mapping_gui.py`, `mapping_audit.py`, and `tests/test_postconversion_handoff_20261123.py`.

User-supplied 2026-11-24 GUI image shows a single source row under a large column group plus blank default 0–1 Matplotlib axes. Local conversion log reported all 1,367 frame endpoints and 725 source area polygons mapped; ETABS returned 55 frames without section assignments; separately saved stage contains 76 base point fixities in a topology-only skeleton. The source EDB SHA and exact folder were supplied privately in the conversation, **not reproduced in this public repository**. Native EDB bytes, current Excel workbook SHA and exact Tk traceback from the user's PC were not accessible.

## Confirmed source-code bug

The immediate V126 property-tree insertion path called `map(str(sr['node_tags']))`, passing only one argument to `map`. This raises `TypeError: map() must have at least two arguments` when creating the first solver-segment child row. Before the correction, `reload()` caught that exception into a status label near the bottom of a scrollable form, **after already inserting one source row** and **before calling `draw_source()`**. The precise one-row/blank-axis screenshot follows from that control flow; no assumption of missing raw ETABS node geometry is needed to explain it.

## Code change and intended semantics

- Replace the broken eager source/solver tree population with on-demand expansion: initially property group roots only, source objects when opening a group, solver segments when opening a source object. This bypasses the malformed map call and avoids eagerly inserting ~14,000 solver rows at startup.
- Maintain `FRAME:` vs `AREA:` namespace, source topology IDs and exact `SOLVER:<tag>` selection mapping. Retain source-only records without constructing fake solver rows.
- `reload()` attempts geometry separately and clears an incompletely inserted tree. Source/geometry errors are displayed in a top banner and bottom status instead of silently leaving an apparently complete but mostly empty mapping.
- Unresolved geometry edges produce an explicit warning. Excel generation remains user-requested only.

No native source, assembled connectivity, support constraint, stiffness, gravity mass, nonlinear section/device activation, ID number, or ETABS workbook changed. All source-only/no-section status remains review-required.

## Tests and limits

Added `tests/test_mapping_browser_lazy_source_20261124.py` with 300 synthetic source objects and 1200 synthetic solver segments plus simulated widget failures, invalid geometry and source-only member. Test-first baseline `7841f79b` produced 4 expected failures, 1890 tests passed/5 skipped. Implementation `eb5a2b88` Green headless pytest succeeded according to GitHub Actions. Final documentation/audit head CI and Windows interactive verification remain to be checked; note final status separately.

Physical contract: **32 physical supports** and **44 wall-mesh transfer points**, not 76 independent foundations. Full gravity `GRAVITY_1.0D_1.0L` differs from NBC 105:2025 §5.2/Table 5-1 seismic mass. Current source 55 unassigned frames require ETABS origin inspection. `SOURCE_CHECKED`, `NUMERICALLY_CONVERGED`, `ETABS_OPENSEES_MATCHED`, `EXPERIMENT_VALIDATED`, `CODE_ACCEPTED` remain **NOT_VERIFIED** for actual structure. Reopen selected export in V126 to verify complete property counts and 3D axes on Windows.
