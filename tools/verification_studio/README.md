# ETABS–OpenSeesPy Verification Studio v2.0

Standalone Windows/Tkinter desktop GUI and CLI for **controlled OpenSeesPy micro-benchmarks**, independent from any ETABS source model or thesis repository. This program does not change the source `.EDB`, ETABS, or thesis program. The actual **native ETABS vs OpenSees** equivalence checks are still separate and require native output files.

## Install / launch

Use your existing Windows conda-forge environment with Python 3.12 and OpenSeesPy installed. On your machine B01–B04 previously passed with OpenSeesPy 3.8.0. Check the module in the exact interpreter you use:

```powershell
conda activate etabs_env312
python -c "import openseespy.opensees as ops; print(ops.version())"
python ETABS_OpenSees_Verification_Studio.py
```

There is no internet access, update mechanism, hidden telemetry, remote upload, or automatic GitHub push in this app. GUI can point to a chosen solver-containing `python.exe`. Alternatively, use the included `START_STUDIO.bat` which uses the activated interpreter.

## Implemented cases and scope

| Test | Specific independent model and reference | What PASS means |
|---|---|---|
| B01 | Existing CSI Example 01 Case II *propped-beam component*; 18 ft, gravity load | Three reactions/forces and force balance match the reported reference; **not the full CSI frame** |
| B02 | 1, 2, 4, 8 elements describing the same propped beam | Reactions and closed-form deflections insensitive to frame split |
| B03 | 2D elastic truss 6 m / 120 kN | Linear axial EA/L calculation |
| B04 | 3D ShellMITC4 wall patch; 1/2/4 meshes, downward 1,200 kN | **Global gravity equilibrium only**; deformation convergence NOT proven |
| B05 | 2D cantilever with finite high-EI root segment | Gravity reaction, root moment and approximate rigid-root flexible-length displacement |
| B06 | 6×6 m ShellMITC4 plate plus 4 perimeter edge beams with shared solver nodes; 4/8/16 meshes | Applied-load conservation and support-force symmetry for the stated fixed corners |
| B07 | 6 m wall shell carried by two bottom frame columns | Wall/column assembly gravity equilibrium and symmetry |
| B08 | 6×4 m shell wall with 2 central mesh cells removed each way (opening) | Net wall geometric area and base equilibrium; not material nonlinear crack/opening strength |
| B09 | Two parallel inclined axial members with distinct supports and shared top node | Analytical **EA/L force-sharing ratio** for identical geometry |
| B10 | Elastic two-bay three-column 2D frame with uniform loads | External vertical equilibrium and symmetric end reactions; **not exact CSI Example 01 reproduction** |
| B11 | One-DOF axial oscillator in kN–m–s; mass in t = kN·s²/m | Analytical first eigenvalue and period |
| B12 | Signed viscous law, C|v|^αsgn(v), α = 0.3 | **ANALYTICAL_PASS only**. It does NOT invoke native OpenSees viscous element, ETABS damper links, or nonlinear time history |

### Native ETABS verification boundary

None of these cases is a source-identical reexecution of the complete CSI verification models (01–15), nor of your 25-story thesis EDB. B01 is only a component of the 3-column Example 01. B06–B09 are dedicated unit assemblies designed to isolate interfaces and support load paths. B12 is formula preflight only. A PASS **never changes the status** of the thesis's 32-foundation-point discrepancy, ETABS shell-edge interpolation, openings, FVD calibration, or first-step nonlinear wall failure.

The old 15-example index is retained on the second GUI tab with their scientific reference-only status.

## CLI

```powershell
python ETABS_OpenSees_Verification_Studio.py --self-test
python ETABS_OpenSees_Verification_Studio.py --list-cases
python ETABS_OpenSees_Verification_Studio.py --cases B05 B06 B07 --output VERIFICATION_RUNS
python ETABS_OpenSees_Verification_Studio.py --run-all --output VERIFICATION_RUNS
python ETABS_OpenSees_Verification_Studio.py --compare-32 "C:\path\to\mapped_reactions.csv" --output COMPARISON
```

Each run stores its own UTC timestamp, exact source SHA256, solver version, case JSON, `results.json`, `metrics.csv`, `manifest.json`, and `report.html`. No output is promoted to acceptance without matching source identity and quantitative metrics. B12 reports `ANALYTICAL_PASS` rather than `PASS`; absent OpenSeesPy reports `BLOCKED`. Each numerical metric uses the user-selectable relative tolerance (default 0.01) and a small per-metric absolute tolerance. **1% is a software diagnostics default, not an engineering code tolerance**.

The supplied example 32-support CSV comparator requires **32 explicit one-to-one mapped rows** and rejects missing or duplicate primary tags; it is DATA_COMPARISON_ONLY_NOT_EQUIVALENCE_PASSED. Do not commit or upload private ETABS model reactions, detailed topology, or real building coordinates to a public repository.

## Known limits and necessary next steps

- This release has been syntax/static checked and B12's analytical test executed here. OpenSeesPy is absent in the build environment, so the new B05–B11 solver cases must be run in your Windows environment. Some shell/constraint combinations may require extra debugging; they are not presented as solver-certified.
- B06 evaluates load conservation and symmetry, **not** native ETABS shell-edge interpolation or complete bending deflection convergence; compare native ETABS beam end shear and plate forces separately.
- B05 uses a very stiff elastic beam segment as a **numerical idealization**, not exact CSI rigid-end offset mechanics. ETABS end offsets change bending/shear stiffness differently than axial/torsional behavior; a separate 6DOF comparison is necessary.
- B08 uses a mesh-void representation without mesh-derived nonlinear boundary cracking or opening reinforcement. It does not validate wall hysteresis.
- B11 uses exact lumped mass and an axial oscillator, not a distributed mass matrix/diaphragm modal benchmark.
- B12 is an equation preflight, not evidence for the thesis FVD exponent α=0.3 parameter or OpenSees implementation.
- Implement native EDB source model provenance, analysis-mesh export, six-force-component reaction comparison, and MESH_04/08/16 subassembly comparison before marking ETABS–OpenSees equivalence.

## Technical references

- CSI, *Software Verification*, Examples 01, 02, 05, 11, 15 (uploaded PDFs, assorted revision numbers). The implemented cases are independent checks rather than faithful full-model transcriptions.
- CSI, *Analysis Reference Manual*, Rev. 23 (October 2025), frame end-offset and edge-constraint sections.
- CSI, [Frame Auto Mesh Options](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/Frame_Auto_Mesh_Options.htm).
- CSI, *Floor Vibration Analysis*, Technical Note S-TN-VIB-001 (January 2024), ETABS original-joint beam mass assignment.
- Nordas, Izzuddin & Li (2025), *Full shell surface coupling along a line with non-conforming meshes*, *Computational Mechanics*, DOI [10.1007/s00466-025-02612-6](https://doi.org/10.1007/s00466-025-02612-6). Nonconforming shell-interface method; not validation of this RC beam–slab application.

**Licensing:** the package contains only original Python scripts and original explanatory text. It intentionally excludes CSI copyrighted PDF manuals/EDBs and all private model-derived exports.
## Troubleshooting: B05–B12 show `No module named 'expanded_benchmarks'`

This error means the **companion Studio Python file is missing from the same folder as the main script**. It does not mean OpenSeesPy is missing when B01–B04 already pass.

On Windows, from your existing repository clone:

```powershell
cd <path-to-your-etabs-opensees-thesis-repository>
git pull origin main
conda activate etabs_env312
cd tools\verification_studio
python -c "import openseespy.opensees as ops; print(ops.version())"
python ETABS_OpenSees_Verification_Studio.py --cases B12 --output VERIFICATION_RUNS
python ETABS_OpenSees_Verification_Studio.py
```

Both `ETABS_OpenSees_Verification_Studio.py` and `expanded_benchmarks.py` **must be present beside each other**. Do **not** copy only the main script into Downloads. When running the GUI, the main window launches workers through the interpreter you selected, but imports the sibling benchmark module from its own source directory. v2.0.1 distinguishes a missing companion module from a missing OpenSeesPy installation and shows a GUI preflight error.

Case B12 is a standalone analytical check and does **not** require OpenSeesPy; if it reports missing OpenSeesPy, that indicates an incorrectly classified failure or an outdated script.

## Recommended: complete single-file Studio (v2.1)

For a one-file application use **`ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py`**. This file includes all twelve B01–B12 benchmark definitions, GUI, subprocess worker, report generation, the CSI reference index, and the 32-support CSV comparison. **It does not import `expanded_benchmarks.py`.** The two-file v2.0 launcher remains available for backward compatibility.

From a freshly updated repository:

```powershell
git pull origin main
conda activate etabs_env312
cd tools\verification_studio
python ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py --self-test
python ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py --cases B12 --output VERIFICATION_RUNS
python ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py
```

You may also save **only that one Python file** to a different folder, including Downloads. Run it with the selected Python interpreter that has OpenSeesPy installed. B12 is analytical-only; B01–B11 require native OpenSeesPy. Do not mistake a missing interpreter dependency for a missing companion program.

Reports are saved in a user-selected local folder and should remain private if they contain project-specific reaction data. A PASS validates only the tested component model and recorded tolerances, not the full CSI verification example or ETABS–OpenSees thesis model.
