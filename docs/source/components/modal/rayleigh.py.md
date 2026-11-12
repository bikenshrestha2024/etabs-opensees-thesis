# rayleigh.py — source documentation

**Python source:** [components/modal/rayleigh.py](../../../../components/modal/rayleigh.py)
**Git baseline content SHA:** 6c51ad3127a799fb4270cb14918ff92cca8bb50d
**Subsystem:** Modal analysis and numerical damping
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the modal implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## November 11, 2026: all-storey and source-model safeguards

The preliminary X/Y Rayleigh runner now calls the all-storey audit helper
([source guide](rayleigh_ledger_audit.py.md)) to reject duplicated or missing
model diaphragm/master-node records and independently reconstruct the
period from every recorded `Wi`, `Fi`, `di`. The original exported V123
compatibility entry is preserved. This is still **not** confirmation that
every seismic-mass-bearing floor was recorded in the original ETABS export.

The `Aw` inputs must be source-matched original workbook values or
explicitly labelled engineering diagnostics. Never infer NBC §5.1.2
acceptance from a continuous-through-height geometric projection.
ETABS model-identity, stiffness/P-Delta, gravity, first-storey wall
openings, centre-of-mass coordinates and torsion-suppressed displacement
must be checked independently before declaring physical equivalence.


## 2026-11-12 full §5.1.1 spreadsheet reconstruction

The native Rayleigh runner now writes live Excel formulas on each `X Rayleigh` and `Y Rayleigh` sheet: columns G/H are respectively `Wi*di²` and `Fi*di`; the sum line and `2*PI()*SQRT(SUM(G)/(9.81*SUM(H)))` independently reconstruct the Python result. Each sheet records reference-force scale and total, **reference force exponent k selected from EMPIRICAL T (not ESM design adopted period)**, state ULS/SLS, source model SHA256, reconciled weight-ledger SHA256 and a structural equivalence warning. Code also writes raw numerator, denominator, reference force sum and exponent in JSON.

The reference-force profile is **not** the finally adopted NBC §6.3 force distribution whenever its k differs from k(T_design); do not silently equate or overwrite them. Reference-force amplitude cancels only for fixed linear stiffness and unchanged shape; check 0.5%, 1% and 2% cases for an unexpectedly nonlinear tangent. For current screenshots, X reference k≈1.542512, Y≈1.518792, whereas NBC adopted ESM X k≈1.740640, Y≈1.710990. Independently reproduce the 25 source `Wi Fi di` rows before accepting the displayed 3.89851s/5.59044s as verified physical periods.

Source: NBC 105:2025 §5.1.1 printed p.28, https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf .
Review: [20261112_RAYLEIGH_PERIOD_AND_NBC_SECTION6_FULL_AUDIT.md](../../../../REVIEW_MAIN/02_ESM/20261112_RAYLEIGH_PERIOD_AND_NBC_SECTION6_FULL_AUDIT.md).
