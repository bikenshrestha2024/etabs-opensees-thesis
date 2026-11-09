# Gravity base-reaction 3D audit

Source: `components/validation/gravity_reactions_3d.py`

This offline module creates a Plotly-based interactive base-reaction display using saved complete ETABS/OpenSees nodal comparison CSV. It does not run ETABS/OpenSees or change the structural model.

## Inputs

* `ETABS_OpenSees_All_76_Nodal_Reactions.csv`, with unique ETABS point names, mapped OpenSees tags, original coordinates and three FZ columns.
* Optional original native ETABS `GetRestraint` audit: columns `ETABS Unique Name`, `restraint_verified`, `uz_restrained`, with explicit Boolean strings. Never derive restraints from reactions.

## Outputs

Node ID labels use Plotly `text`; detailed mapped reactions and restraint evidence
use `hovertext`. These channels must remain separate. The HTML trace regression
in `tests/verify_gravity_reactions_3d.py` checks both using the actual Plotly trace
constructor; it does not establish native ETABS/OpenSees agreement.

* `Gravity_Base_Reactions_3D.html`: offline HTML, dropdown for ETABS reactions, OpenSees original support model, OpenSees continuous wall-base model and both signed differences.
* `Gravity_3D_Restraint_Audit.csv`: point mapping, native restraint status, reactions and differences.
* `Gravity_3D_Restraint_Audit.json`: totals, native restraint coverage and validation warnings.

## Engineering constraints

* ETABS reported FZ=0 does not imply an unrestrained analysis mesh joint; native source DOFs and MPC associations require separate verification.
* The two user-facing strategy names are `ETABS Reaction Validation` (legacy solver ID `ETABS_SOURCE_SUPPORTS`) and `ETABS Node Position / Continuous` (legacy `CONTINUOUS_WALL_BASE_FIXED`).
* The latter is a deliberate idealized support sensitivity study, not certified ETABS validation.
* Raw results and legacy output IDs remain unchanged; renaming never alters gravity loads, stiffness, support flags, or seismic mass.
* Differences at individual wall mesh nodes are insufficient evidence of erroneous load transfer unless integrated wall and column region totals and source restraint mapping are considered.

## Reproducibility

```powershell
conda install -c conda-forge plotly
python Run_Offline_Gravity_3D.py
```

No native ETABS installation is required. The optional restraint CSV is accepted only as user-provided native evidence; this module does not extract or independently prove its provenance.
