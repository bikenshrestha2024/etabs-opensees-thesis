# nbc105_horizontal_input.py — horizontal earthquake input provenance and vertical applicability

Source: [components/nonlinear_time_history/nbc105_horizontal_input.py](../../../../components/nonlinear_time_history/nbc105_horizontal_input.py).

Purpose: explicitly record NBC 105:2025 §4.3 vertical-action triggers, §9.3.2.2 common lower paired scale and §9.3.2.3 XY/YX input mapping. X/Y translational DOFs are 1/2 in OpenSees; no Z DOF pattern is applied in the two-component research setup. Per §9.3.1.1 the model remains fully three-dimensional with torsion.

Inputs and output: five verified feature answers (unknown supported), orientation, raw record A/B filenames, source acceleration units, common scalar dimensionless pair scale, record dt. Outputs are a recorded command-manifest dictionary; no design approval. Invalid source units and already-scaled status block duplicate scaling.

Engineering restrictions: support input UniformExcitation returns relative nodal displacements, not absolute. The recorded structural model, masses and constraints require independent checks.

Tests: `tests/verify_nbc105_horizontal_input.py`. See [full clause guide](../../../programs/33_NBC105_XY_YX_VERTICAL_AND_SCALE_GUIDE.md).
