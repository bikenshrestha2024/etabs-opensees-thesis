# MRSM response spectrum / CQC review
**RV-RSA-001:** P0 OPEN_HIGH — ETABS native comparison missing
**RV-RSA-002:** P1 INVESTIGATE — base-shear scaling, edge drift and graph provenance

## Supplied ULS values (2026-11-11)
X centered Vraw=22586.5843613 kN; scaling S=1.1041063928. Y centered Vraw=16748.1890576 kN; S=1.5793191122. X and Y +5%/-5% accidental eccentricities yielded essentially unchanged reported **global base-shear magnitude**, which does **not** imply unchanged torsion/edge drift or independently verified eccentricity enforcement. The scaled shears are approximately 24939 kN (X) and 26450.7 kN (Y); verify precise values and target definition from source saved cases.

## Engineering interpretation
CQC components are unsigned/nonconcurrent response envelopes; do NOT draw them as one simultaneous physically deformed shape, add signed mode peaks, or compare to a time-history instantaneous deformation. Distinguish floor force accumulation from **recovered cut** storey shear. Drift is a response quantity and its force scale application is governed by the actual NBC analysis procedure; GUI legend indicating 'force-only scale excluded' must be validated against governing provisions and the intended design/use state.

## Next native tests
- Source-native ETABS mass-source, damping, spectra ordinates, g scaling, eccentricity, load cases, 5% breadth, mode combination, torsional modes, PDelta/effective stiffness, direction and response combination.
- Compare identical model states X/Y E0, Eplus, Eminus for base shear, independently recovered storey shear, roof and interstorey displacement, drift at four edges, modal participation and period.
- Show ULS and SLS separately. SLS blank plot signifies MISSING_SLS, never zero. Legend must not duplicate 18 curves where only six exist. 
- Include source EDB hash and CSV/header/unit normalization; ETABS comparison empty/MISSING_ETABS is not validated.

**Acceptance:** ETABS response rows present and same-state comparison valid; deviations explained physically before downstream LTH/NLTHA reliance.
