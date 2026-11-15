# V162 — Unified Plotly member-prefix selection and responsive inspector

## Evidence and scope
The user-supplied Windows Chrome screenshot (15 November 2026) shows `OpenSees_Structural_Elements_By_Storey.html`: Story 9, COLUMN, ETABS unique object ID 1162, topology preview tag 9001 and a separate displayed OpenSees element tag 9048. The pre-existing ID selector defaults to Node selection and sits above a separate story/property filter. There is no direct source-qualified prefix/number selector. Original ETABS IDs, topology tags, actual assembled OpenSees solver tags and **display aliases are separate namespaces**; do not rewrite solver tags to improve appearance.

## Code changes
- Compact primary toolbar in *all root-level generated Plotly HTML 3D and load/floor views*: Prefix B/C/BR/CO/BT/CT/FVD/BRB/SW/FL → optional Storey → verified display element number. Shows `display_label · ETABS unique source ID`; selectable roles come **only from source-typed `display_category`**, including explicit `display_member_roles` CO/BT/CT overrides already approved in the saved working config. Generic braces are **not** assumed to be cap, belt, damper or BRB members.
- `Highlight` delegates to the original ETABS source-ID match logic (no conversion of alias into OpenSees solver integer). `Focus` uses original mapped node XYZ for 3D Plotly axis bounds; Zoom and camera presets remain available. A missing role (often FVD/BRB) clearly shows `no source-verified members`.
- Existing original ETABS object ID, OpenSees topology preview tag, *assembled* OpenSees element tag, ETABS point, OpenSees node and Zoom to Node controls remain in the standard accessible **Advanced ID & node** disclosure, rather than being deleted. Responsive CSS, accessible select labels, keyboard Enter, clearer status.
- Original Plotly HTML re-injection removes prior selector and CSS by exact stable IDs and replaces each once, so re-running conversion doesn't stack three toolbars. No changes to the separate Tk/Matplotlib V126 3D module; its existing filter stays unchanged.
- Exact source category `FVD` or `BRB` can acquire a **display-only** prefix. A generic frame/link never becomes a FVD or BRB without original explicit source category evidence.

## Engineering preservation and native acceptance
No ETABS `.EDB`, source Excel, FVD/BRB physical assignment, wall/brace/slab topology, material section, solver tag, end release, constraint, load, mass or analysis case was altered by this UI patch. Display alias `CT2501` does not mean source solver tag 2501, and cannot certify device or outrigger physical connection behavior.

**Validation targets:** focused synthetic Python/OpenPyXL test generates 3 Plotly views and tests distinct member aliases, unchanged Excel ID columns, re-export idempotency, and JS syntax (when Node is available). UI interaction in the user's Chrome/Spyder Windows environment remains a **manual acceptance gate**, and the application requires regenerating the saved 3D HTML views from the updated repo; old already-generated local HTML does not update itself.

**Status:** SOFTWARE_UI_CHANGE_ONLY / NATIVE_ETABS_PHYSICS_NOT_TESTED.
