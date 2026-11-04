# ground_acceleration.py — recorders, ground support input and absolute floor acceleration

**Source:** [ground_acceleration.py](../../../../components/nonlinear_time_history/ground_acceleration.py).

**Purpose:** For OpenSees `UniformExcitation` two horizontal DOF support input, the node acceleration recorder returns **relative** structural acceleration. Ground acceleration is supplied as a specified `Path` series in `g` (matched waveform) and converted once to m/s². An absolute horizontal floor-acceleration estimate must **add** the corresponding support input: `a_abs,nodeX=a_rel,nodeX+a_ground,X`, likewise in Y.

**Functions and parameters:**

- `_sample_path(values,dt,time_s)`: linear time interpolation of a sampled Path, zero outside the recorded interval. Requires positive finite dt and at least two sample values.
- `applied_ground_acceleration(records,time_s,orientation,excitation,additional_spectral_scale)`: pairs original A/B source `g` or `m/s2` inputs and returns applied global X/Y support acceleration for XY or YX. `excitation` is either XY, X, Y or ZERO diagnostic mode; it never applies unsupported vertical Z.
- `relative_to_absolute_floor_acceleration(node_relative_xyz,ground_xy)`: adds measured uniform-support X/Y input to nodal relative response. Rotational, Z and multisupport effects are excluded.

**Runner output fields:** `ground_AccelX_m_s2`, `ground_AccelY_m_s2` (global support inputs), `Storey_N_UX_relative_accel_m_s2`, `Storey_N_UY_relative_accel_m_s2` and new `Storey_N_UX_absolute_accel_m_s2`, `Storey_N_UY_absolute_accel_m_s2`. A per-case `Ground_Acceleration_Recording_Method.json` records source units, conversion, orientation, scale and method restrictions.

**Caveats:** These equations apply only to common **UniformExcitation** support motion. Do not apply them directly to multiple support excitations, SSI/input incoherence, or absolute recorders. Confirm the transient solver starts at t=0 after gravity preload and the `Path` interpolation agrees with the native OpenSees version. They do not calibrate a concrete wall, damper or dynamic model.

**Primary reference:** [OpenSees UniformExcitation pattern](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/uniformExcitationPattern.html), which states that nodal response is relative to the ground. [OpenSees Path timeSeries](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/timeseries/pathTimeSeries.html). **Test:** `tests/verify_nltha_ground_acceleration.py`.

[Stage 35 complete NLTHA workflow](../../../programs/35_SOIL_C_PRIMARY_NLTHA_RUNBOOK.md).
