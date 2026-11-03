# Stage 03 — wall openings and E-SFI mesh fidelity

The exploratory runner now accepts `wall_openings_manifest` pointing to JSON containing `wall_openings` with entries `id, plane (XZ/YZ), constant_m, horizontal_min_m, horizontal_max_m, z_min_m, z_max_m, source`. Rectangular opening footprints are checked against every assembled shear-wall quad. Any wall quad occupying the declared void **blocks** analysis; an empty manifest is marked `UNVERIFIED_NO_DECLARATIONS`, not approved.

This stage checks source mesh geometry, **not** experimental E-SFI convergence. Still required: calibrated single-panel cyclic loops, C/T/U core cross-section loading, coupling beams, boundary reinforcement and nonlinear torsional response. References: Kolozvari et al. (2023) https://doi.org/10.1016/j.engstruct.2023.116700; Rezapour et al. (2026) https://doi.org/10.1007/s10518-025-02353-0.
