# Four-lot ETABS reference import

OpenAI Codex desktop extended the shared workbook reference reader and CLI
from main commit `daef7574401cf5090b746b5bfaefb8d1a5ae28c8`. The same
worksheet-owner catalog still verifies each workbook's identity. The first
and second lots retain their existing JSON command behavior.

The third and fourth lots add joint, wall, frame, shell and station tables.
SQLite storage streams the full selection through the common parser and
records repeat positions without merging distinct source samples at the
same normalized value. The SQLite manifest and database are published as
one completed local directory. Regression tests cover the legacy workflow,
unit conversion, source row identity, filtered aliases and interruption
before publication.

The reference has no production solver write path. The 32 physical
foundation supports, 44 wall-mesh points, full 1D+1L gravity benchmark and
NBC Table 5-1 seismic weight remain separate from workbook results. Source
EDB identity, complete native case coverage and ETABS/OpenSees numerical
equivalence require their existing evidence. The private workbooks and
generated reference are excluded from the commit.


## Fourth-lot split-source handoff (2026-11-27)

Editor: OpenAI ChatGPT (GPT-6.2). Base commit `3ea8b60b53f4af9e3ab30127aed5fea3e6277ddc`.
Read-first contract checked. The earlier FIRST, SECOND and THIRD LOT
integration PRs #231–233 and the post-merge replay record are retained.
The full fourth lot and two candidate fourth-lot parts were supplied.
Python/container startup returned a client error when attempting to open
the new inputs; the alternate file reader provided no worksheet content.
Consequently the fourth-lot cell scan, sheet ownership, row counts,
content fingerprints, equivalence of the split parts to the original
and engineering diagnostics are NOT_VERIFIED. No source results were
substituted and no numerical or solver code changed.

The existing CLI accepts an arbitrary list of input paths; the canonical
reference importer rejects a supported table with multiple workbook owners.
For the split form, use five complementary files (lots 1, 2, 3 and lot 4
parts 1 and 2), not those files plus the unsplit fourth lot. This is a
candidate selection until the actual worksheet-owner catalog confirms
disjoint supported tables. If a single supported worksheet was divided
by rows across parts, the existing importer does not implement a general
row-shard merge; retain both parts, audit them separately and resolve the
partition using source keys and units before importing. Do not rename
worksheets just to bypass the ownership check.

From the repository root, using actual local source paths and new private
output locations:

```powershell
$lots = @(
    "FIRST LOT.xlsx"
    "SECOND LOT.xlsx"
    "THIRD LOT.xlsx"
    "FOURTH LOT part 1.xlsx"
    "FOURTH LOT part 2.xlsx"
)
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-files $lots --audit-output "../FIVE_FILE_AUDIT.private.json"
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-files $lots --table-index-output "../FIVE_FILE_CATALOG.private.json"
python tools/REGISTER_CURRENT_ETABS_TABLES.py --analysis-reference $lots --reference-storage sqlite --reference-output "../FIVE_FILE_REFERENCE"
```

Replace the example names with exact paths. Review exit codes and audit
completeness before publishing the local reference. Compare the original
fourth lot with its parts in a separate audit, not a joint production
selection. Keep prior audit artifacts, inputs and outputs private and
unchanged. These commands and ownership rules were checked against the
current CLI and importer source; they were not successfully executed on
the new files. This is documentation-only, no new regression or native
solver execution. 32 physical + 44 mesh points PRESERVED; full gravity
1D+1L PRESERVED; NBC Table 5-1 seismic weight PRESERVED; 12 m X-wall
policy PRESERVED. All native model and code acceptance gates remain open.


## Actual fourth-lot part 1 source review (2026-11-27)

Editor: OpenAI ChatGPT GPT-6.2; base `1ee136881f5093299bb381e73ed3f7920962dc70`.
Read-first root AGENTS, physical-model contract, project skill, core rules,
engineering gates, migration/program index, current table reader, guide and
related tests inspected. Earlier first/second/third-lot records and split
handoff retained unchanged. The supplied part 1 was actually opened with
Python openpyxl read_only=True, data_only=False and all four worksheet data
streams and populated values inspected. Local audit counted source rows,
non-null values, case/type/step, numeric field ranges, missing/zero/nonzero
counts and duplicate candidate keys. The four table schemas match the
existing canonical importer: Integrated Wall Reactions, Element Stresses -
Area Shells, Element Strains - Area Shells, Element NL Energy By Group.
No repeated candidate keys, missing numeric response fields, formula
markers or standard error markers were detected. Shell case/story/design
type counts agree; the source file title does not establish model identity.
The earlier lots and part 2 were not supplied again in this turn, so a
complete five-file import and ownership comparison were not rerun.

The source shows shell envelope groups with nonzero directional responses
but all-zero principal/equivalent response fields, and all-zero reported
nonlinear group-energy fields. These require output availability checks,
not a physical zero-demand or inactive-device conclusion. Extend the
existing reference parser with bounded per-group field-availability
counts, without changing source values or adding solver write paths.
No envelope reconstruction, group summation, reaction fitting or
source/model changes. The local helper was tested on actual extracted shell
strain and energy rows with independent per-column count reconciliation and
source-row digest verification; the complete repository regression suite
and native solver were not executed locally (container GitHub DNS unavailable).
Added regression assertions for duplicate aliases, prefilter scope,
missing versus zero and nonzero group energy. CI verification is required
for this integration. Raw model outputs, hashes, and private row-level
evidence remain local.

32 physical + 44 mesh points: PRESERVED; gravity 1D+1L: PRESERVED;
NBC Table 5-1 seismic weight: PRESERVED; two 12 m X-wall policy: PRESERVED.
Source workbook scan is evidence, not EDB binding. Numerical convergence,
ETABS/OpenSees agreement, experiment validation and NBC acceptance remain
NOT_VERIFIED.


## Actual fourth-lot part 3 source review (2026-11-28)

Editor: OpenAI ChatGPT GPT-6.2; base `26eb7b85500712e12604b99eeeccc54e361239b8`.
Read-first root AGENTS, physical model contract, dedicated skill, core rules,
engineering gates, migration/program index, canonical reader, guide and test
inspected. Preserve first/second/third-lot PRs #231–233 and part-1 PR #234.
Part 2 remains unverified in the earlier split handoff. Only part 3 was freshly
streamed with openpyxl read_only=True, data_only=False, reset dimensions. Both
column and brace station force sheets were fully extracted into private SQLite
with original worksheet positions, typed counts, per-case extrema and source
fingerprints. Independent replay of row digests, database integrity, source
hash stability, candidate keys, exact case/step identity, object/position
coverage and numeric completeness passed for observed rows. Trailing optional
Location was blank, not an invalid force field. Part 1's existing inventory was
compared for case-name coverage. No fresh combined six-file scan performed.
Raw numerical values, hashes, object IDs and records remain private.

Extend the canonical importer with prefilter frame station coverage diagnostics;
the same helper passed on every actual extracted data row. Added importer
regression fixture for missing coverage, repeat positions with distinct
payloads, null Location and separate station coordinates. Full suite cannot
run locally because GitHub DNS failed; CI required. No change to source data,
physical parameters, factors, solver, acceptance or ownership.
32 physical + 44 mesh points: PRESERVED; gravity 1D+1L: PRESERVED; NBC Table
5-1 seismic weight: PRESERVED; 12 m X-wall policy: PRESERVED. Native EDB binding,
axes/end-zone equivalence, ETABS/OpenSees matching, NLTHA convergence and NBC
acceptance NOT_VERIFIED.

Candidate split selection now comprises six files: FIRST LOT, SECOND LOT,
THIRD LOT, FOURTH LOT parts 1, 2 and 3. Add part 3 to the prior explicit
PowerShell array and choose NEW private audit, catalog and SQLite destinations.
Never also select the unsplit fourth lot. Verify worksheet ownership; overlapping
row-sharded tables require source reconciliation rather than arbitrary renaming.


## Cumulative source status and beam / part 2 audit (2026-11-28)

Editor: OpenAI ChatGPT GPT-6.2. Base `f6261ff635c00e2180ebc5ac501ce26c1ecac506`. Retain all previous audit
records without replacing any private result dataset. Read-first model
contract, canonical reference/beam readers, source guides and tests reviewed.
PR #235 (part 3 station diagnostics) merged after ten successful CI runs;
PR #236 (beam native unit-row recognition) merged after five successful CI
runs. Neither changed the solver, support, load or geometry contracts.

- FIRST / SECOND / THIRD LOT: prior actual full-cell audits and PRs #231–233
  retained; worksheet dimensions reopened, not claimed as fresh full-cell scans.
- FOURTH LOT part 1: previous actual full scan, PR #234.
- FOURTH LOT part 2: recovered from private file library, all worksheets and
  populated values streamed with openpyxl read_only=True/data_only=False.
  Both shell and frame joint force tables extracted and independently replayed
  from private SQLite. Source hash stable; no repeated candidate keys or
  invalid force components. Their exact case-step sets match. All shell
  position/step keys match the earlier shell stress keys in source order
  after excluding its Design Type attribute. Both sets of force positions
  reconcile exactly to the corresponding actual SECOND LOT topology
  endpoints/corners. The new helper was executed on every extracted force
  row with that reopened topology, with no unresolved source positions.
  Added an importer regression fixture to exercise mismatches, shell-edge
  exclusion and prefilter scope. CI required for repository verification.
- FOURTH LOT part 3: earlier actual full scan retained; PR #235 merged.
- FOURTH LOT part 4: no separately named source located in current attachments
  or the inspected recent library listing. Do not infer its content or alias
  Beam Element 1 to part 4.
- Beam Forces Element 1 latest: actual complete cell scan and private
  SQLite replay passed; the beam worksheet reaches Excel row cap and ends
  mid-member. No full multi-part beam consolidation demonstrated. Native
  table-specific kN/m units supersede Program Control display units.
  PR #236 recognizes the exact native units row; the gravity-only importer
  remains strict, not an all-case reader. The all-case audit is kept separate.
- Beam Element 2 / 3 latest: listed in prior library; not freshly scanned
  or reconciled with the new part 1 in this turn.

All proprietary rows, actual source hashes, local paths and extrema remain
private. Combined source-bound production import and native EDB / axis / case
identity, force-equilibrium and ETABS/OpenSees comparison, NLTHA and NBC
acceptance NOT_VERIFIED. 32 physical + 44 mesh points, 1D+1L gravity, separate
NBC Table 5-1 seismic weight and 12 m X-wall policy preserved.


## Beam Element 2 additive source audit (2026-11-28)

Editor: OpenAI ChatGPT GPT-6.2. Baseline `8d8f19be89e461861ab73c022343884bafa94eef`.
PR #237 merged after ten successful CI workflow runs. Earlier FIRST, SECOND,
THIRD, FOURTH LOT parts 1–3 and Beam Element 1 audit history is retained.
The new Beam Element 2 workbook was fully streamed with Python/openpyxl
read_only=True and data_only=False; original worksheet positions and raw
values extracted privately. Source SHA stable, SQLite integrity passed,
no repeated candidate keys or missing/nonfinite numeric result fields.
The source has the native row-limit split and includes multiple case types.
Strict case gate reproduced on the actual first record; the exact-case
selection helper was independently replayed on all extracted Beam Element 1
and 2 records and reconciled with SQLite counts, without relabeling any case.
Opt-in CLI case projection extends the canonical beam importer; the strict
gravity GUI and default case behavior remain unchanged. Selected vs scanned
counts, excluded case names/counts and row-cap indicators are recorded,
including sheets with no selected rows. Added importer regression for
explicit selection, strict failure and zero-selection publication guard.
Actual workbook audit and helper replay are distinct from full integration
tests. Full repository checkout unavailable due to GitHub DNS; CI required.
Beam Element 3 remains a separate unverified source in this turn.
Combined native EDB identity, axis/offset equivalence, load transfer, solver
convergence and NBC acceptance remain NOT_VERIFIED. No source rows, model
fingerprints, extrema or local paths published.
32 physical + 44 mesh points, full 1D+1L gravity, separate NBC Table 5-1
seismic weight and two 12 m X wall policy PRESERVED.


## Beam Element 3 additive source audit (2026-11-28)

Editor: OpenAI ChatGPT GPT-6.2. Baseline `1364f80e28efb38d4a1c97fdf9c024f3488f0253`.
PR #238 merged after five successful CI runs. All earlier lot and beam
audits retained. Actual Element 3 workbook was opened and fully streamed
using Python/openpyxl read_only=True, data_only=False. Original row positions,
values, per-case extrema and fingerprint retained privately. All worksheets
scanned; unchanged source hash and SQLite integrity verified, no internal
duplicate native keys, missing numeric response values or observed
object/case-step gaps. This is a source audit, not native solver acceptance.
Extend the existing beam consolidator with opt-in all-case exact native
identity and payload checks. Preserve strict gravity and explicit case
projection modes, source hashing and case counts. Added regression fixtures
for distinct case types and analytical elements, exact overlap, conflict
within legacy tolerance, native units and mutually exclusive flags. Full
repository checkout is blocked by DNS in the local runtime; CI required.
Raw workbooks, fingerprints, row payloads and extrema remain private.
32 physical supports + 44 wall mesh points, 1D+1L gravity, separate NBC
Table 5-1 seismic weight and two 12 m X walls PRESERVED. Native EDB binding,
axis/offset compatibility, OpenSees comparison, solver convergence and NBC
acceptance remain NOT_VERIFIED.

Actual three-file extraction replay subsequently completed: all observed beam/case-step station sets reconcile, all beam-labeled SECOND LOT frame element positions are represented, and every observed position matches that topology. Exact native overlap payloads agree, gravity projection reconciles and no distinct native gravity keys collide under the legacy gravity key on these observed rows. Original source positions and overlap aliases retained in private SQLite. The actual-data replay is independent of the repository CLI; the new CLI is not claimed executed against the workbooks. Distinct all-case output filenames protect legacy gravity lookup. Full combined native model import and solver equivalence remain NOT_VERIFIED.

## Combined source reference and gravity cut check (2026-11-28)

Editor: OpenAI ChatGPT GPT-6.2. Baseline `00a800aaae0f76d86deb70caf75370198627b63e`. PR #239 merged after five successful CI runs. All nine original sources reopened for worksheet inventory and SHA-256; previous full-cell audits preserved. Actual FIRST LOT Story Forces, SECOND LOT joint topology and THIRD LOT Joint Reactions streamed read-only; exact full-gravity unstepped combination and source joint identities reconciled to the base cut at displayed precision. Observed zero/nonzero reaction counts agree with the declared support/mesh counts, but they do not themselves identify OpenSees supports. The exact new gravity helper was executed on these actual rows and six focused assertions (valid residual, duplicate, mismatched label, repeated cut, envelope, missing component). Private coordinates, IDs, force values and hashes are excluded from Git. Extend the existing reference CLI to orchestrate separate analysis and beam owners in a staged publication; supplemental regression fixtures authored, full CI required. Full production combined invocation not yet executed locally: full checkout blocked by GitHub DNS. Native OpenSeesPy/XARA unavailable; no native solve, force equivalence, NLTHA or NBC acceptance claim. 32 physical + 44 mesh points, 1D+1L, NBC Table 5-1 and 12 m X walls preserved.


## Fifth LOT additive reference import (2026-11-28)

Editor: OpenAI ChatGPT GPT-6.2. Baseline `e8f0eb22c3bcd6e3f1bdcf3a6dd11ee61f48cac2`. Existing PRs #231–240
and prior private audit history retained. The new native workbook introduces
six shell/diaphragm schemas. Actual smaller diaphragm CM/center and drift
tables inspected read-only; repeated floor mass and center fields agree
at exported precision, and zero-average drift records are retained.
Extend the canonical SQLite importer without introducing a new reader,
preserve declared distributed shell units and mass/inertia units, retain
blank acceleration envelope sides and reference-only status. Reuse the
shell topology diagnostic and add a prefilter CM/center consistency check.
Supplemental importer regression authored; CI required. No native EDB
binding or solver equivalence asserted. 32 physical + 44 mesh, full 1D+1L
gravity, distinct NBC Table 5-1 seismic weight, two 12 m X walls PRESERVED.
Earlier separately named fourth part 4 still not located; do not silently
alias the fifth lot or unsplit fourth lot. Raw rows and source hashes remain
private. Full combined source invocation and native acceptance NOT_VERIFIED.


## Sixth LOT additive native reference import (2026-11-28)

Editor: OpenAI ChatGPT GPT-6.2. Baseline `86acccf7be7af82923168f7998ef3df285878215`. Prior lots and PRs
#231–241 retained. Actual Sixth LOT all worksheets and every populated cell
streamed read-only without formula evaluation; private SQLite row replay,
source fingerprint and integrity verified. Base reactions match the exact
joint-reaction case-step set. The full-gravity six-component joint resultant
was independently reconstructed at the reported origin; displayed residuals
remain private. Assembled joint mass identities/coordinates match topology;
omitted base topology and repeated floor mass/inertia fields reconcile with
earlier exports. This is not an inference of native restraints or accepted
mass matrix. Analysis messages only report informational elapsed times; do
not infer convergence. Extend existing SQLite importer for three native
schemas and prefilter diagnostics, reusing common-origin resultant math.
Supplemental regression authored, full CI required. Local full checkout
blocked by DNS; source replay is actual data, not full combined production
CLI invocation. 32 physical supports + 44 mesh, 1D+1L full gravity, separate
NBC Table 5-1 mass and two 12 m X walls PRESERVED. No source rows, model
fingerprints or machine identifiers published. Native EDB binding,
pointwise reaction equivalence, M0–M6 NLTHA and NBC acceptance NOT_VERIFIED.


## Combined reference consumer and split GUI routing (2026-11-28)

Editor: OpenAI ChatGPT GPT-6.2. Baseline `fe604158faca7f3ce13d40f74c58dd2bfbb91671`. Read-first contracts checked: 32 physical + 44 mesh points, full 1D+1L gravity separate from NBC Table 5-1 seismic mass, two 12 m X walls preserved. Exact active source recovered from GitHub CI artifact. All eleven source fingerprints reverified. Actual production CLI completed on original SECOND LOT, SIXTH LOT and Beam Element 3; proposed reader verified actual reference bytes and exact mass/base/gravity/modal projections. Actual full split selection resolved the unique Joint Reactions worksheet. Full eleven-source CLI invocation tracked independently. Red/green focused regression: 73 tests and 16 subtests passed. Full CI required. Native ETABS/OpenSeesPy/XARA unavailable; no numerical, physical or code acceptance inferred. No private workbook records or hashes published.


## Assembled input mass comparison consumer (2026-11-28)

Read-first physical constraints retained. Compared archived actual assembled model input against verified Sixth LOT Assembled Joint Masses using canonical story mass plan. Actual CLI verification on original workbook subset passed, along with focused 36 tests and 23 subtests (red regression reproduced missing function first). Source and model hashes are private; no mass values published. Archived comparison is not a current model identity or solved mass matrix check. No changes to gravity, supports, mass assignment or stiffness.
