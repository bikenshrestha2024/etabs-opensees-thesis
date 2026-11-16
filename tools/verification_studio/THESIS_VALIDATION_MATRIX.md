# Verification Studio → thesis workflow acceptance map

**Scope:** This is a separate independent validation harness, not a substitute for `components/model/assembly.py`, CSI native `.EDB` reruns, or the complete 25-storey thesis acceptance procedure.

## Case groups and evidence status

| Thesis workflow | Component tests | What they can establish after a native PASS | Additional acceptance evidence still required |
| --- | --- | --- | --- |
| Units and gravity mechanics | B01, B03 | Beam/truss element reactions under controlled loads; kN–m–s sanity | Verified ETABS source loads, joint assignments, offsets, six-DOF equilibrium |
| Beam subdivision/mesh | B02, B05 | Identical propped-beam response across subdivisions; approximate stiff-end component | ETABS native frame auto-mesh; actual offset rigid-zone factor; real joint releases |
| Shell and slab transfer | B04, B06 | Shell gravity equilibrium; shared beam–shell node assembly | Native ETABS shell-edge constraints; slab 04/08/16 cell distribution and local beam moments/shears |
| Wall/opening/base transfer | B07, B08, B09 | Simple shell-column/opening/parallel support force checks | Full shear-wall geometry, openings, boundary DOFs, 32 physical support actions compared at equivalent locations |
| Global frame/modal | B10, B11 | Two-bay frame equilibrium and simple lumped-mass axial eigenvalue | 3D mass source, rigid diaphragm, Ritz/eigen mode basis, modal mass distribution |
| Nonlinear damping/device | B12 | Only an **analytical** odd-force/velocity-law precheck for C and alpha | Native OpenSees viscous link hysteresis and time-history; matching ETABS link; dimensional calibration |

## How to run on Windows (from repository root)

```powershell
git pull origin main
conda activate etabs_env312
cd tools\verification_studio
python ETABS_OpenSees_Verification_Studio.py --self-test
python ETABS_OpenSees_Verification_Studio.py --run-all --output VERIFICATION_RUNS
```

Alternatively, double-click `START_STUDIO.bat` after activating the appropriate interpreter in a command prompt.

The `VERIFICATION_RUNS` directory is ignored by Git. Never commit generated native model/reaction/mesh evidence or source EDB/XLSX files publicly. A passing simple component case may be logged as `NATIVE_OPENSEES_BENCHMARK_PASS` only for the exact model, metrics and tolerance included in its report; do not promote to `ETABS_OPENSEES_EQUIVALENCE_VERIFIED`.

## Next gates before the 32-foundation-reaction discrepancy can be closed

1. Prove source EDB hash, ETABS release, source static gravity case, loaded area panels, frame end offsets, shell edge constraints, native mesh and support DOFs.
2. Compare source/slab assembly with 6 m × 6 m floor bay for 04, 08 and 16 meshing; inspect transfer at actual shell and parent beam stations, never assume equal shell cell forces imply equivalent ETABS load paths.
3. Export full six-component nodal reactions from ETABS and OpenSees and map all 32 physical foundation coordinates. Treat 76 and 97 as separately constrained sensitivity models, never additions to physical foundation count.
4. Compare 18 frame-only versus 14 shell-only groups and explain previously observed 18,648.51 kN load redistribution with local beam/wall forces and displacement evidence, not force-matched overrides.
5. Run modal, MRSM, linear TH, nonlinear TH independently, with native solver versions and source hashes; block any accepted M0–M6 full-record result until complete and reviewed.

## Audit interpretation

The previous user's v1 B01–B04 runs passed on Windows OpenSeesPy 3.8.0. This checked-in **v2** is the preserved program; v1 passes do not constitute reruns of v2. The v2 build ran the five offline Python tests plus self-test and B12 analytical preflight. The B05–B11 native solver cases are **not yet independently run** by this change. GitHub Actions on this directory only executes **offline** checks and deliberately cannot certify native ETABS or OpenSees.
