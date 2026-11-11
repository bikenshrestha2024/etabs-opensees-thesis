# P1 — Gravity Matplotlib node selection and native reaction equivalence

Status: OPEN_HIGH.

## Observed
Gravity reaction plot displays a set of support node tags without a filter or multi-node selection control. The current screenshots show vertical Rz reactions but not a native ETABS/ODE comparison at each support.

## Engineering judgment
Reaction bars are associated with OpenSees node tags, not guaranteed ETABS point object names. The choice of 32 ETABS nonzero-reaction nodes versus 76 source supports is a *diagnostic modeling hypothesis*, not an approved physical change. Global force equilibrium can pass even when individual support load paths are wrong. The new source log reports 311367.313600 kN ETABS vs 311367.313880 kN OpenSees in one 32-support 1D+1L diagnostic, but simultaneously labels the per-node comparison SCREENING_ONLY / NOT_ESTABLISHED. This cannot be conflated with the separate 76-support AS_CONFIGURED MRSM preload.

## GUI acceptance
- Provide searchable, multiselect support-node IDs, a select-all/clear option, and persisted selected node list.
- Permit sorting by node tag, Rz magnitude, absolute/relative ETABS–OpenSees error; use category grouping (core, perimeter, wall support) only when source mapping exists.
- Plot selected-node reactions and individual 6-DOF components in consistent axes/units; empty or nonexistent nodes show an explicit message.
- Show physically collocated ETABS joint IDs, mapping source, unit, load case, support strategy, and exact EDB hash.
- Export a per-node CSV, full unfiltered workbook, selected plot, manifest, and outlier list into each Gravity case folder. Never mislabel one set's results as another.

No GUI implementation is claimed in this issue report.
