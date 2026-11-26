# Gravity, Linear, and Nonlinear case evidence

Editor OpenAI Codex desktop. Base `35479e0ec0ac6901b6afecc151712d34400209f4`. Added an explicit elastic settings reader, improved the Gravity picker and Linear launch with the selected export, and corrected case-local modal and MRSM packaging. Original support and load assumptions were preserved. Supplied solver runs and prior ZIPs were kept in place.

The native OpenSees diagnostic rebuild used the documented ULS approximation and the original assignment workbook. The settings omit native rigid offsets. The subsequent gravity comparison screened the 32 physical supports and remains unverified for structural equivalence. The case-local results and source evidence are private.

The production NLTHA window now opens the selected model through the runtime launcher. The readiness dashboard starts the wall-probe picker in the selected project's nonlinear stage and reports the count of workstreams with no discovered files independently of sign-off claims. Both time-history recorders use the solver's verified support tags. The shared NLTHA tolerance remains 1e-6 by default with an explicit 1e-7 selection.
