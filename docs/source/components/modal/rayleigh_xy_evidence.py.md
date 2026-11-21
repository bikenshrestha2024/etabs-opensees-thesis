# Independent Rayleigh X/Y evidence reconstruction

Canonical module: `components/modal/rayleigh_xy_evidence.py`

## Ownership and source

This pure-Python evidence checker consumes saved **native solver results** and calls the common NBC Clause 5 `rayleigh_period_s` calculation in `components/nbc105/clause_05_dynamic_characteristics.py`. The active production Rayleigh run remains in `components/modal/rayleigh.py`; this module does not alter its forces, stiffness, masses or solver settings.

[REF NBC 105:2025 §5.1.1 printed p.28] For each direction, `T = 2π sqrt(sum(W_i*d_i²) / (g*sum(F_i*d_i)))`, with `d_i = lateral_loaded_i - gravity_equilibrated_i`, `g=9.81m/s²`. Inputs must include X and Y, explicit ULS/SLS state, model/EDB/story ledger SHA256, positive weights, floor identities, physical floor centre-of-mass translations and torsion suppression.

A separately solved perturbed amplitude profile can check that `F` and `d` scale together and that the period is amplitude-invariant within documented **diagnostic**, non-normative tolerances. An ETABS reference period may be displayed as a comparison, not an engineering equivalence determination.

## Testing and limitations

`tests/test_rayleigh_xy_evidence.py` covers hand-computed single-DOF `T=π`, X/Y coverage, changed floors, invalid hashes, wrong COM basis and amplitude invariance. CI: `.github/workflows/six-dof-common-cut.yml`.

**Not verified:** whether ETABS and OpenSees have identical source mesh, diaphragm constraints, seismic mass operator, P-Delta tangent, stiffness modifiers, end zones, gravity baseline or native eigenperiod. No native ETABS/Windows analysis is run by this module.

[REF `docs/validation/20261118_RAYLEIGH_RETAINED_DOF_CORRECTION.md`; `REVIEW_MAIN/02_ESM/20261119_RAYLEIGH_MASS_DISTRIBUTION_PHYSICAL_GAP.md`]
