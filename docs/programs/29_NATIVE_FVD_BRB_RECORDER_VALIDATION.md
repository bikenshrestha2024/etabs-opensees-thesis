# 29 — Native FVD and BRB recorder benchmark

**Run on Windows in the user's verified Python 3.12 OpenSeesPy/conda-forge environment:**

    python 29_NATIVE_DEVICE_BENCHMARK.py --output "D:/Thesis/Device_Benchmark"

The script constructs independent 3D two-node FVD and corotTruss BRB models and applies two seconds of sinusoidal external force. It records accepted displacement, velocity and queried OpenSees element forces. The FVD profile uses K=2000 kN/m, Cd=20 kN(s/m)^0.3, alpha=0.3; BRB uses an illustrative Steel02 law (Fy=350000 kN/m2, E0=200000000 kN/m2, A=0.001 m2). **These are arbitrary isolated numerical smoke-test values, not experimental calibration and not the thesis FVD settings.**

Supported documented recorders: twoNodeLink basicForce, basicDisplacement, localForce; corotTruss axialForce and deformations. Actual return shapes must be checked in the installed binary, especially for material stress/strain queries. The report includes raw force-velocity work but deliberately does NOT certify damping energy, sign convention, stiffness accuracy, BRB fatigue or physical specimen validation.

**Required next experiment:** independently benchmark a real FVD under cyclic controlled displacement using its measured force, relative velocity and stroke data, and calibrate Maxwell K, Cd, alpha using an actual measured file. Verify balance F*(udot) = elastic spring storage rate + dashpot dissipation using a consistent resisting-force sign; inspect full hysteresis and peak forces. For BRB, use coupon/core cyclic loops, explicit plastic displacement, compressive/tensile strength factors and fatigue life.

This test is not run by GitHub Actions because the current CI environment lacks a native OpenSeesPy binary. On this assistant's container the native package is also unavailable. Never report successful execution without generated Native_Device_Benchmark_Report.json and matching solver log.

References: [twoNodeLink](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/TwoNodeLink.html); [corotTruss](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/CorotationalTruss.html); [OpenSees element recorder](https://opensees.github.io/OpenSeesDocumentation/user/manual/output/ElementRecorder.html).
