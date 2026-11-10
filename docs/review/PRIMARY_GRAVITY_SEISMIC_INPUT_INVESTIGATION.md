# Primary gravity and seismic input investigation

Scope: user's supplied V03/V04 gravity evidence, original assignment and full
ETABS tables, ESM logs and original linked calculator output. Local engineering
files and personal paths are excluded from this public change.

## Why ETABS equivalence is not validated

The original 32-node result is now the main gravity case, as requested. Its
legacy internal identifier remains `ETABS_NONZERO_REACTION_DIAGNOSTIC` to keep
saved results, environment settings and manifests compatible. Its user-facing
classification is primary; numerical success still does not imply equivalence.

The supplied 32-node table has 32 matched joints and total difference only
0.000279549 kN (rounded ETABS export). At joints 263/264, however, native ETABS
Fz is 14748.5222 kN and OpenSees Fz is 17789.787978 kN: +3041.265778 kN,
20.6208%. This is an actual distribution difference, not a summation error.

The native instrumented rerun reproduced the saved solution exactly. All 14262
elements returned global resisting forces. Signed element/applied/support
vertical balance at 11097 joints has maximum absolute residual 3.97e-10 kN.
The solver therefore balances its own load path; it does not reproduce the
native ETABS load path at every support.

Confirmed differences needing engineering reconciliation:

- ETABS assignment table: automatic end offsets, rigid factor 1. The inspected
  OpenSees elastic frame creation uses centroid-node PDelta transformations
  without joint offsets. Clear-length **weight** correction did not implement
  the corresponding end-zone **stiffness**. This can change load sharing; no
  unverified stiffness correction was introduced here.
- The 32-node model releases other source base points. Native joint 718 has
  zero Uz; OpenSees has -0.867204 mm there. Zero native Fz does not demonstrate
  an unrestrained DOF. The requested 32-node main case is retained explicitly.
- The equivalent nodal load ledger applies 1923.444378 kN directly at base
  elevation. A recovered interface force just above base is 309443.869502 kN;
  adding the directly applied base load gives the full reaction. Comparing
  that interface alone with total foundation reaction would be incorrect.
- The native `Element Forces - Beams` sheet has 1048576 rows, Excel's limit.
  Coverage must be established from split exports/native tables, not assumed.

The offline audit mapped 1101 source joints over Base and all 25 storeys and
exported per-joint Uz, per-storey differences and native top/bottom story P.
Interior joints have transferred element forces and displacements; they are
not foundation supports. New gravity exports record full frame/shell vectors,
joint balance and recovered floor interface Fz. No missing force is fabricated.

The old scorecard also looked under the comparison root while the selected
run's actual direct evidence was nested under that run. Lookup now prefers
the exact run and does not recursively select another 32/76/97 result.

## Why period boxes were blank

The original engine writes labelled outputs to `ETABS Sync`. The explicit
reader previously required `SCALING SUMMARY`, so a populated original
calculator could not supply its adopted periods through that route.
The reader now accepts the original layout with source attribution.

Separately, Aw inferred from OpenSees geometry could already be populated,
which prevented the GUI's linked-workbook fallback from running. Matching
original linked evidence now takes priority even when geometric Aw exists.
Rebuilt exports can also have a different output root from older ESM runs;
an explicitly registered, hashed audit can be reused across those roots only
for the same current EDB hash and state.

Original calculator adopted values: X 2.03856740011866 s and
Y 1.9219797767063125 s; Aw-X 1.9582936288088642 m²,
Aw-Y 2.2030803324099724 m². The provisional geometric Aw-X used in the
screenshot gives about 2.05312 s instead. These sources are now distinguished.
Adopted design periods, static Rayleigh periods and measured modal periods
remain separate. An empty modal-reference field is not filled with an
empirical or workbook period and labelled as a measured eigenperiod.

## GUI and exports

Use the existing support selector plus **View selected 32 / 76 / 97 saved
case** to view the fingerprint-matched saved run. Missing/stale cases require
rerunning that condition. ESM's existing full review ZIP includes ETABS-linked
and OpenSees evidence separately; its plot picker includes solved deflection,
shear and drift profiles. MRSM has a manual full evidence ZIP button and its
existing Matplotlib/Excel and deformation viewers now use the solver's output
root. Existing native ETABS comparison tables remain independent.

Local `project_sources.private.json` binds explicit source paths and SHA256
to the exact EDB SHA256. A changed source is rejected; another model is not
silently reused. `OPENSEES_PROJECT_SOURCES` can select this registry after
moving/installing the code. The registry is excluded from Git.

## Remaining acceptance work

No source EDB, source workbook, load, material, mass or selected-case restraint
was modified. Native ETABS/seismic reruns and visual end-to-end comparison of
all new controls remain pending. The master architecture migration remains
incremental; this is not a whole-repository semantic review or completion claim.

References: [OpenSees eleForce](https://openseespydoc.readthedocs.io/en/latest/src/eleForce.html),
[joint-offset transformation documentation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/geomTransf/Linear.html).
