# ETABS 23 analysis verification examples

Scope: all 15 supplied CSI verification PDFs. This is a benchmark selection and reference audit. The published runs were reviewed; the native models were not rerun. The supplied Analysis folder contains PDFs only.

| Example | Published verification problem |
| --- | --- |
| 01 | Plane frame, concentrated and uniformly distributed gravity loads |
| 02 | Three-storey plane frame, response spectrum |
| 03 | Three-storey plane frame, historical code-based static lateral loads |
| 04 | One-storey 3D frame, response spectrum |
| 05 | Three-storey 3D braced frame, axial-only members and response spectrum |
| 06 | Nine-storey, ten-bay plane frame, eigenvalues |
| 07 | Seven-storey plane frame, gravity and lateral analysis with periods, spectrum and time-history comparisons |
| 08 | Two-storey 3D frame, constant-amplitude response spectrum |
| 09 | Unsymmetrical two-storey 3D frame, two horizontal spectrum directions |
| 10 | Three-storey plane frame with ADAS devices, nonlinear time history |
| 11 | Three-storey plane frame with viscous dampers, nonlinear time history |
| 12 | Pounding of two plane frames with gap elements, nonlinear time history |
| 13 | Base-isolated two-storey 3D frame, bidirectional nonlinear time history |
| 14 | 3D frame with friction-pendulum isolators, bidirectional nonlinear time history |
| 15 | Wall shell configurations under static lateral loads, ETABS–SAP2000 displacement comparisons |

## Benchmark order for the thesis

1. Reproduce Example 01 first. Match the support conditions, beam span loads, units, local axes and output stations. Table 1-1 reports an ETABS and theoretical match for moments and shears, including end-J moments of -4,050.00 for the concentrated load and -4,860.00 for the uniform load in the example's units. Rigid joint offsets are excluded by this benchmark's specification.
2. Add a controlled beam–column end-offset benchmark using the CSI Analysis Reference Manual §7.10. Check bending, shear, axial and torsional response under independent unit loads. Test physical end releases at the support faces separately.
3. Build a beam–slab strip with shared nodes as a separate case. Match native ETABS and OpenSees analysis connectivity, mesh, section properties, constraints, load and output stations. Record applied-load totals, support reactions, deflections and beam shear/moment. Evaluate a collinear shell edge constraint as a separate variant if the source uses that assignment.
4. Run the matched gravity case for parent beams 251 and 343, and compare the 32 mapped support reactions. Preserve the source and generated-node IDs, the boundary conditions, and the station origin. Compare signed reactions and their individual errors as well as the aggregate force.
5. Extend to modal and spectrum checks using Examples 06 and 09, viscous-damper response using Example 11, and elastic wall-shell displacement using Example 15. Example 03 exercises historical load procedures; verify the thesis's NBC 105 implementation against its own requirements. Example 15's inter-program displacement comparisons do not qualify nonlinear concrete wall behavior.

Each run record should identify the source PDF and revision, model/export identity, units and sign convention, expected quantity and station, numerical tolerance chosen before the comparison, observed error, and result.

## Follow-up verification against the supplied benchmark review

The native files are installed under `D:/ETABS23/Verification/Analysis Examples`, separate from the PDFs. The folder contains Example 01, 02, 05, 11a/b, and the Example 15 variants among others. Use working copies for native reruns.

An independent Example 01 beam-theory calculation matched 20 published shear and moment ordinates for B1 at the five reported stations under both load cases. Using the 216 in span, the left prop reaction is 3wL/8 under the uniform load and 5P/16 under the centered point load. The midspan shear for the point load uses the value immediately to the right of the load. Only the analytical targets have been reproduced. Neither solver has been rerun.

Example 02 uses a 24 in top-of-column rigid offset in the theoretical idealization and compares periods and mode shapes. It is a coupled modal end-zone check. Keep separate unit-load tests for the axial, torsional, shear and bending effects. Example 05 compares periods and selected member forces for axial-only members. Example 11's published comparison uses exponent 1; the thesis exponent 0.3 requires its own force–velocity and time-history benchmark.

Evidence status per check: REFERENCE_DOCUMENTED for a traced published target; BENCHMARK_REPRODUCED after running and matching the specified model and quantities; ETABS_OPENSEES_EQUIVALENCE_PASSED only for the explicitly compared model, cases, response quantities and predeclared tolerances. Example 01 analytical target reproduction alone leaves both software runs pending. The 32-support building comparison remains pending.
