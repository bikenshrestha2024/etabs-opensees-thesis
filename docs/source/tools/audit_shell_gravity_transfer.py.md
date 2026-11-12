# audit_shell_gravity_transfer.py — floor-shell load-vector patch review

**Implementation:** [tools/audit_shell_gravity_transfer.py](../../../tools/audit_shell_gravity_transfer.py). Python 3.12, standard library, Windows Spyder compatible.

## Source-code finding
The existing components/model/assembly.py converts each floor mesh-cell uniform area load into four nodal forces Q_i=q*A/4. Those nodal forces act at the nodes of OpenSees ShellMITC4; the plate/shell stiffness and connected beam/wall nodes determine the subsequent load distribution. No additional beam line load is synthesized for the same pressure. The load vector is exact for regular parallelograms but not general distorted quadrilaterals.

## Independent patch test
Integrate F_i = integral_A N_i q dA using 2x2 isoparametric Gauss quadrature and the actual node coordinates. For a rectangle 2m by 3m with q=5 kN/m2, each nodal force is 7.5 kN. For the distorted quad (0,0),(2,0),(1.5,1),(0,1), q=1 kN/m2, A=1.75m2, the consistent loads are (11/24,11/24,5/12,5/12) kN, versus four equal forces 0.4375 kN. The global load is identical but the beam/wall load distribution can differ.

## Run
Use Python command: python tools/audit_shell_gravity_transfer.py --model-json <path-to-OpenSees_Complete_Model_Data_V118.json>. In Spyder without CLI arguments, choose the model JSON through the file picker. A new Shell_Load_Patch_Review_TIMESTAMP.json is written outside the original model export (existing paths refused). Original ETABS EDB, model JSON, Excel, and loads remain unchanged. Recorded: SHA256, number of checked cells, cell-orientation problems, distorted-cell count and up to 100 largest nodal-load discrepancies.

## Engineering gates not satisfied by this arithmetic alone
1. Verify each source ETABS area assignment is Uniform (Shell), Uniform to Frame (Shell), or another load type; beam tributary load must not be duplicated.
2. Verify correct shared-node connectivity of shells, frames and walls, including edge constraints and diaphragm UX/UY/RZ (NOT vertical UZ).
3. Compare a single slab, then a slab + beam + wall benchmark with identical ETABS and OpenSees shell thickness, section stiffness, support DOFs and load application, recording beam moments/shears, wall actions, reactions and deflections.
4. Validate actual source mesh and geometry, inverse Jacobian/element orientation and mass source before any production adjustment.

## Sources
- CSI Floor Auto Mesh Options: https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Floor_Auto_Mesh_Options.htm
- CSI Shell FAQ (Uniform Shell vs Uniform to Frame): https://web.wiki.csiamerica.com/wiki/spaces/kb/pages/2001188/Shell%2BFAQ
- OpenSeesPy ShellMITC4: https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html
- Dvorkin, E.N. and Bathe, K.-J. (1984), A continuum mechanics based four-node shell element for general nonlinear analysis, Engineering Computations 1:77-88, DOI https://doi.org/10.1108/eb023562
- Bathe, K.-J. and Dvorkin, E.N. (1985), A four-node plate bending element based on Mindlin/Reissner plate theory and a mixed interpolation, DOI https://doi.org/10.1002/nme.1620210213
- MacNeal, R.H. and Harder, R.L. (1985), A proposed standard set of problems to test finite element accuracy, Finite Elements in Analysis and Design 1:3-20, DOI https://doi.org/10.1016/0168-874X(85)90003-4

**Engineering status:** patch-vector review only, not ETABS physically validated or code accepted.
