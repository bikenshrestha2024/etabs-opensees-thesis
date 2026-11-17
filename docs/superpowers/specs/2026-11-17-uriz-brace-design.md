# Uriz nonlinear brace implementation and benchmark design

Status: proposed design for researcher approval; no implementation or validation claim.
Approval scope: isolated planar (2D) global-buckling adapter and benchmark only.
The 3D/source-building contract below is a future requirement list, not an
approved or sufficiently resolved connection formulation.
Target: PR #112, starting from fb62f59a39c0ba29680004a3876e1e2dc4fc6325.

## Intent and constraints

Develop the global cyclic-buckling formulation described by Uriz, Filippou and
Mahin (2008), DOI 10.1061/(ASCE)0733-9445(2008)134:4(619), first as an isolated
OpenSeesPy brace. Then expose an explicit opt-in research building mapping only
after its domain, release and load-transfer checks pass. Existing elastic source
mapping and unrelated frame/wall/device gates stay intact. This is ordinary
steel bracing, not a BRB. No project steel, imperfection or connection calibration
is inferred from the publication.

Private supplied PDF SHA256:
a87846fe633fb9a04a22897c3f9f93a373ed3c6f89754ff197e5920d8034751a.
Do not commit the supplied PDF or extracted full text to the public repository.

## Approaches

1. Recommended: force-based fiber beam-columns, corotational transformation,
   explicit midpoint geometry and released physical end rotations. This follows
   the paper and can reuse/refine the existing section machinery.
2. Axial truss with a fitted cyclic axial law: needs independent force-history
   calibration and cannot represent the paper's distributed axial-flexural
   mechanism. Keep the existing exploratory route distinct.
3. Shell/solid brace model: potentially resolves local buckling, but requires a
   different geometry/material validation program and much greater cost. Outside
   this paper-based implementation.

Only approach 1 meets the requested paper-based scope. Selection is proposed,
not recorded as approval of this design document.

## Evidence extracted from the uploaded paper

- pp. 620–621: force-based distributed plasticity, small deformations in the basic
  system with large-displacement corotational transformation; at least two
  elements and a middle node to permit brace lateral displacement.
- pp. 622–623, Fig. 3: compact 4-inch extra-strong pipe benchmark; length 118.4 in;
  reported yield stress 24 ksi; E=29,000 ksi; hardening ratio 0.003; 2 radial by
  30 circumferential fibers. Nominal pipe size is not its actual outside diameter.
- pp. 622–624: parabolic initial camber; imperfection magnitude influences first
  buckling. The study explores a broad range; these are sensitivity inputs, not
  measured project imperfections.
- p. 624 correlation setup: two elements, three integration points per element,
  initial midpoint camber 0.0005 L. Mesh studies also use seven integration points.
- p. 628 recommendations: two elements; midpoint camber 0.0005–0.001 L; three
  integration points. Accurate local strains can require more elements, especially
  for pin-fixed supports. Do not equate global-force convergence to strain or
  fracture convergence.
- pp. 626–628: local buckling and low-cycle fracture are not implemented by this
  model. The noncompact HSS counterexample illustrates its limitation.

The paper does not provide a complete machine-readable cyclic loading history,
experimental response vectors, every Steel02 transition/isotropic parameter,
or measured project steel/connection data. These remain explicit missing inputs.
No exact experimental reproduction may be claimed from these values alone.

## Existing code and ownership

EXTEND existing `components/sections/definitions.py` geometry/steel-section
machinery where suitable. Its SHS builder already uses multiple rectangular
fiber patches and finite GJ, despite an imprecise short docstring; inspect area
and second moments before reuse. Do not reuse its expected-strength default
as a measured paper or project value.

First implement a standalone planar builder using a 2D, three-DOF domain,
private midpoint nodes, physical pin translations and free end rotations. No
torsional DOF exists in this first benchmark. Its domain must be owned by the
benchmark process, not shared with the building.

A dedicated ordinary-brace helper under `components/sections/` should own input
validation, local geometry, end connections and generated-tag manifest. Add its
individual source guide and module registry entry. Reuse existing material
validation helpers only when their contracts fit; BRB naming must not leak into
ordinary brace classification.

`components/model/assembly.py` currently uses Steel01/corotTruss for exploratory
hinged braces and rejects reviewed nonlinear released braces. Integrate the new
helper only after isolated checks; do not merely delete that rejection.

## Adapter contract (proposed engineering choices)

- Units: kN, m, s; stresses kN/m2. Convert paper inches/ksi once at the fixture
  boundary and record original units. Require all material numbers explicitly.
- Inputs: physical endpoint coordinates and source IDs; source-compatible local
  basis; section geometry or audited fiber data; E/Fy/hardening/transition and
  isotropic parameters; imperfection amplitude/direction; subdivision and
  integration counts; release vectors; unique caller-owned tags.
- Initial geometry: transverse local displacement `4*delta*s*(1-s)` for normalized
  station s. Require even subdivision count >=2 to include exact midpoint.
  Validate finite values, nonzero length, transverse direction and noncolliding
  tags before mutating the solver domain.
- Future 3D geometry (not first-stage scope): corotational transformation per segment. A finite section
  GJ is needed internally; zero source torsional transfer is represented at the
  external connection, not by removing internal torsional stiffness everywhere.
- Connection: coincident private end nodes tied in translation to physical joints;
  end bending rotations remain independent. Resolve otherwise free torsional
  rotation with an explicit internal datum/compatible constraint after checking
  that it introduces no physical-joint moment transfer. Arbitrarily oriented 3D
  members require a correct local-axis treatment, not global-axis equalDOF guesses.
  Unsupported release patterns or conflicting preexisting constraints fail closed.
  This 3D connection design remains unresolved: before implementation, enumerate
  one-end versus both-end torsion releases and specify finite-rotation-compatible
  constraint equations/handler. Require arbitrary-orientation and rigid-rotation
  invariance tests. Do not invent a global rotational fixity in the first stage.
- Interior brace nodes remain brace-private: never attach the buckling midpoint
  to floor diaphragms or nearby shell nodes by coordinate proximity. Intermediate
  physical source connections require a separately reviewed segmented-member map.
- Preserve physical source length/weight and existing tributary mass/load ledger;
  geometric imperfection must not silently add physical mass. Source loads are
  measured against the original straight source member until a documented source
  convention says otherwise. Future mapping must conserve both resultant force
  and moment under child-axis transformations; this needs its own design review. Distributed gravity
  loads must transfer to the actual generated segments once, with equilibrium
  checks. Do not copy the old beam-segment loads onto every new child.
- Outputs: source IDs, all physical/private nodes, elements, transformations,
  material/section/integration tags, local basis, release representation and
  input/source/software hashes. Preserve original exception and failed step;
  retry only in a new solver domain.

## Benchmark ladder and acceptance

1. Deterministic solver-free validation: reject invalid geometry/materials/tags;
   verify midpoint camber, endpoint coordinates, fiber A/Iy/Iz convergence and
   physical source mapping. Mock command checks only verify API construction.
2. Native planar elastic checks: straight pin-ended member axial stiffness EA/L
   and endpoint equilibrium; released end moments below 1e-6 times max(1 kN-m,
   peak axial force times length). Use separate planar models for each section
   bending axis, not an unrestricted strong-axis claim in 3D. Record theoretical
   Euler reference pi^2*EI/L^2. Do not infer critical load from solver failure.
   Instead compare subcritical lateral amplification of the explicitly parabolic
   initial geometry against an independently derived elastic beam-column solution
   at 0.1, 0.3 and 0.5 times the Euler reference. Verify the reference derivation
   and mesh refinement before asserting a tolerance pass. Provisional software
   tolerances: relative axial stiffness/equilibrium 1e-5; refined subcritical
   lateral response within 5%. Critical-load extraction remains a later test.
   These tolerances are proposed software checks, not NBC acceptance criteria.
3. Native cyclic smoke: explicit displacement reversals with recorded axial
   reaction, midpoint lateral displacement, end moments, local strains and work.
   Show compression strength loss and tension recovery without inventing fracture.
   Separate synthetic protocol from the Black et al. experimental history.
4. Sensitivity: 2/4/10 elements, 3/7 integration points, both transverse planes
   and documented imperfection amplitudes. Report force/energy/strain differences;
   do not silently select the best-matching parameters after seeing results.
5. Experimental comparison: obtain original Black et al. UCB/EERC-80/40 pipe
   dimensions, cyclic protocol and response data; alternatively digitize paper
   figures with a reviewed axis calibration, points and uncertainty record.
   Keep digitized figure agreement separate from raw-data validation. Set the
   experimental error tolerances before comparison after data quality is known.
6. Building integration: fresh-domain reduced assembly tests for arbitrary 3D
   orientation, source releases, gravity/mass conservation and ID crosswalks;
   only then a source-matched building diagnostic. No automatic NLTHA_READY.

## Delivery and execution

Standalone API, source guide, deterministic regressions, native benchmark CLI,
input/output JSON manifest and comparison CSV/plots. The benchmark stores exact
solver version, Git SHA, inputs, failure/convergence history and units.

Native Windows invocation will use the user's
`D:\condaenvs\etabs_env312\python.exe` from an updated checkout. Cloud-native
execution is separate evidence if a compatible solver can be installed; never
report cloud checks as a run of that Windows environment.

First deliverable is a global-buckling research adapter and analytical/native
benchmark evidence. Experimental curve reproduction is conditional on traceable
data. Local buckling, fatigue fracture and project qualification remain separate
work rather than capabilities implied by the paper title or a successful solve.

## Builder review disposition

A separate builder review identified unresolved 3D torsion/release constraints,
load conventions and critical-load extraction. Approval is therefore requested
for the isolated planar benchmark only. No automatic source-building adapter or
nonlinear readiness promotion is included. Experimental reproduction still
requires the missing original data or reviewed figure digitization.
