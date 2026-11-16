# Gravity support discrepancy — partial-run comparison repair (2026-11-16)

## Status

**Reporting defect corrected; structural cause still UNVERIFIED.** This change is
not a claim that ETABS and OpenSees support reactions match. No solver supports,
wall elements, masses, stiffness, applied loads, or mesh constraints were modified.

### Defect and repair

`join_source_etabs_reactions()` previously required the available solver-reaction
union to include all 76 ETABS source support tags. With only the primary 32-support
run solved, 44 genuinely absent solver reactions caused an exception. This stopped
the comparison exporter before it could show the ETABS source's 76 rows.

The revised function joins the *full ETABS source-support audit* with the union of
actually solved reaction rows. Unsolved case values remain `null`, not zero. The
summary separately reports how many source support rows have no solved values,
and which of the 32/76/97 cases are actually present. Duplicate solved node tags
are rejected. Source nodes at or below the classification tolerance are identified
consistently with the original source audit.

Regression test: `tests/test_gravity_partial_source_comparison.py`.

## Evidence supplied with this review (not committed)

Three ETABS 23 beam-force spreadsheets, all for `1. DL + LL`:

- `Element Forces Beam 1 DL+ LL(2).xlsx`: Stories 15–25; 3,729 data rows,
  329 story/member combinations.
- `Element Forces Beam 2 DL LL(2).xlsx`: Stories 6–16; 3,729 rows,
  329 story/member combinations.
- `Element Forces Beam 3 DL + LL(2).xlsx`: Stories 1–6; 2,040 rows,
  180 story/member combinations.

The spreadsheet records are ETABS **beam internal forces** by station; they are
not ETABS joint restraints, joint reactions, OpenSees force outputs, or a basis
for modifying six-DOF fixity. The overlapping story ranges must be deduplicated
by the tuple (Story, Unique Name, Output Case, Station) and verified for numeric
agreement before any combined force comparison. Retain local-axis and station
conventions, member end-offset assumptions, and sign convention.

## Source-identity / acceptance gates

1. Read native `PointObj.GetRestraint` and, where applicable, analysis mesh
   restraint/constraint assignments directly from the exact source EDB. Do not
   infer a free joint from ETABS `FZ=0`.
2. Export the **complete base joint reaction table** for `1. DL + LL`,
   including ETABS Unique Name, three force components and three moments,
   together with the source connectivity mapping and source restraint flags.
3. Solve each of 32/76/97 scenarios *independently* under the same gravity
   profile, with an audited node-to-node load and restraint map. Keep 32 as
   a **diagnostic boundary-condition case** until source equivalence is proven.
4. Compare total gravity equilibrium, individual base support forces, integrated
   column and wall-region reactions, and connected beam/wall element end forces.
   Separate shell nodal force transfer from frame end actions; check diaphragm,
   end-offset, wall internal mesh tie and base level handling.
5. Validate source-vs-target units, local axes, frame element mapping, station
   positions, section properties, self-weight inclusions/exclusions, dead and
   live load assignments. Distinguish applied load mismatch from redistribution.
6. Reject a structural-equivalence PASS if the above physical checks are missing,
   even if the total support reactions agree or the run converges.

**Important:** The existing hardcoded user-confirmed 32-node tag set should
not be silently reused for another model export. Neither the present beam
spreadsheets nor this code repair certifies the 32-node fixity as native ETABS.

## Validation

The branch includes a regression test for 32-only availability and duplicate
solver rows. Native ETABS 23 / OpenSeesPy engineering solves require the user's
Windows model exports and are not executed by this repository edit.
