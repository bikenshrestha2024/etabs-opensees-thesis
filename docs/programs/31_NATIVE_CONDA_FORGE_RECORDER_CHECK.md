# Native conda-forge Tcl recorder test

This workflow uses conda-forge opensees (the Tcl executable) with isolated FVD twoNodeLink and Steel02 corotTruss models. It applies harmonic load over 2 s and tests element basicForce/basicDisplacement or axialForce/deformations plus nodal displacement/velocity. All kN-m-s input parameters are illustrative and not calibrated to any test specimen.

After the native solver completes, a Python verifier checks finite scalar samples and chronological alignment. It computes signed force-velocity work but does not infer an approved force sign or dashpot dissipation, and does not verify manufacturer force/stroke or BRB fatigue capacities.

A successful Tcl run is only underlying native command compatibility. OpenSeesPy recorder behavior on Windows must still be checked independently with 29_NATIVE_DEVICE_BENCHMARK.py. Literature and documented commands: https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/TwoNodeLink.html and https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/CorotationalTruss.html.
