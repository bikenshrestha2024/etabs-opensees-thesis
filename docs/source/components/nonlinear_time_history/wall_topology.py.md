# wall_topology.py — RCC core opening presence and geometry audit

**Implementation:** [wall_topology.py](../../../../components/nonlinear_time_history/wall_topology.py).

The current thesis system contains openings. A `THESIS_NLTHA` run requires a **nonempty ETABS-reviewed `wall_openings_manifest`**; `verify_project_opening_manifest_required` checks source presence (not yet geometry), while `write_opening_report` compares each rectangle with the assembled wall quads and blocks filled/not-bordered openings. A missing or empty manifest can no longer be interpreted as an approved core mesh for thesis-intent analysis. Exploratory probes may run with explicit `UNVERIFIED_NO_MANIFEST` status.

**Limitations:** Only axis-aligned rectangular XZ/YZ void checks. Irregular re-entrant core junction geometry, inclined panels, coupling-beam cyclic behavior, web/flange corner continuity, reinforcement and actual capacity still require direct ETABS/native validation. Sources are the user's actual ETABS files and official OpenSees 3D E-SFI material/element documentation; do not infer physical openings from paper models.

**Tests:** [verify_wall_openings.py](../../../../tests/verify_wall_openings.py).

[Full P0 audit](../../../review/01_WALL_GEOMETRY_MATERIALS_FIRST_STEP.md).
