# Nonlinear time-history review
**RV-NLTH-001:** P0 OPEN_BLOCKER — first-step X wall nonfinite response
**RV-NLTH-002:** P0 OPEN_BLOCKER — project wall/frame/device calibration
**RV-NLTH-003:** P0 OPEN_HIGH — full Soil C XY/YX record suite and source provenance

Historical first X transient failed near t=0.005 s. Element tags 110280 / 112778 were seen with bad wall outputs *after solver failure*; postfailure nonfinite localForce is a localization clue, not proof of causation. Need exact mapping to ETABS AREA:354 / AREA:482, four-node quad orientation, FSAM material, boundary conditions, diaphragm, gravity and numerical algorithm state.

**Required minimum cases:** fresh-domain ZERO, X, Y, XY and YX at identical gravity/mass/stiffness/material settings; capture last ACCEPTED-step element forces, energy, strains, gap, nodal displacements, solver error and source hashes. Compare smaller dt and compatible solver fallback without hiding physically invalid model. Do not relabel successful zero motion as validated earthquake response.

**Materials:** actual reinforced-concrete wall opening geometry, wall vertical/horizontal rebar, coupling beams, confinement, boundary elements, verified ConcreteCM/SteelMPF/FSAM behavior, axial load variation, device FVD/BRB calibration. IS 13920 detailing and NBC 105:2025 structural performance must be reviewed independently; generic PEER research parameters are not automatically acceptable for this structure.

**Ground motions:** eight Soil C paired records (six research near-field, two far-field), both orthogonal XY/YX orientations; matched inputs already Acc(g) and nominal additional scale 1.0. Verify historical SeismoMatch factor logs, 0.33–3 constraints, Gorkha 322.94-s versus original 120-s provenance and Loma Prieta one-sample mismatch. Full M0–M6 112 configurations ×2 orientations=224 intended analyses, none inferred complete from existing trial logs.

**Acceptance:** full converged paired histories, actual validated material/geometry, drift/strain/energy/device demands, code acceptance review and reproducible signed evidence. No automatic solver convergence = design pass.
