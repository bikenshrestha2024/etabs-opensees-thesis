# Time-history GUI, structural interpretation and public-repository security review

**Date:** 2026-11-11. **Evidence tier:** source-code change and limited deterministic CI, NOT native ETABS/OpenSees model verification. **Reference:** NBC 105:2025, the active project acceptance gates, and original SeismoMatch/PEER evidence.

## Linear versus nonlinear response-history analysis

### Linear (LTH)
An elastic or linearized structural model solves, approximately,

    M u_ddot + C u_dot + K u = -M Gamma a_g(t)

where M is mass, C is the selected viscous damping matrix, K is the linear/effective stiffness, Gamma maps ground acceleration to the model, and u is displacement **relative to the moving ground** under OpenSees UniformExcitation. Bidirectional cases apply two independent components at the same instant; XY and YX interchange the assignments, not the time order. OpenSees `algorithm('Linear')` changes the numerical solution algorithm, **not** nonlinear material objects into linear elements. LTH must use a verified elastic/linearized material and section model, effective stiffness, diaphragms, stiffness modifiers, P-Delta treatment, gravity state and correct mass source.

Linear output: roof displacement, floor displacement, interstory drift, story/base shear and member actions versus time; no concrete cracking progression, yielding, cyclic stiffness degradation, residual drift due to permanent material strains or damper-specific nonlinear constitutive behavior unless explicitly modelled by the governing equations. Recovered action combinations for linear TH must follow the approved NBC design basis and cannot be inferred from a histogram alone.

### Nonlinear (NLTHA)
A geometrically and materially nonlinear model solves the incremental equilibrium equation

    M u_ddot + C u_dot + f_internal(u, history, materials, devices) =
        -M Gamma a_g(t) + other_applied_loads

using iteration at each time increment and a state-dependent tangent stiffness. It can reproduce yielding, concrete cracking/crushing, confinement, cyclic deterioration, buckling, energy dissipation through properly parameterized nonlinear devices, P-Delta instability and residual displacements **only where the model explicitly provides and validates those effects**. A convergence message does not validate a physical material model.

NLTHA requires material-specific citations and verification (frame fibers, actual wall geometry/openings and reinforcement, SHS braces, BRBs, nonlinear FVD links), gravity/P-Delta and seismic mass compatibility, units, a verified record set and bounded numerical step sizes. Cases with non-finite output, incomplete duration, lost convergence or missing project material evidence remain diagnostic/failed; never put them in an accepted suite average. For this thesis, elastic wall shells with exploratory nonlinear frames do not constitute a calibrated nonlinear RCC core-wall study.

### Damping, periods and time integration
Distinguish **NBC adopted directional T1** used in seismic design from **modal eigenperiods** measured from the stiffness/mass state and from **two Rayleigh calibration periods** used to define the damping coefficients. Both X/Y modal eigenperiods, Tn90, damping on inspected modes and participation must be calculated or checked on the current physical state. Device damping must not be double counted by applying Rayleigh damping to explicit FVD/BRB regions.

For typical two-term Rayleigh damping, C = alpha_M M + beta_K K_reference and modal damping is zeta(omega) = alpha_M/(2 omega) + beta_K omega/2 (for modes consistent with that reference stiffness). For nonlinear committed stiffness, `K_reference` and coefficient placement must be reported; damping may evolve in ways not represented by the simple constant-K expression. Review **all inspected modes** against the project/code damping limit, not merely the two calibration frequencies.

A 0.5-second diagnostic run of Hector Mine or Loma Prieta is not a complete earthquake-history analysis. It cannot establish code-based peak drift, displacement, base shear, collapse margin, material demand or numerical stability over the remaining 39–45 seconds. The GUI and evidence output must retain `TRUNCATED_DIAGNOSTIC_NOT_CODE_ACCEPTANCE`, requested/integrated steps, full record duration and input hashes. Do not silently change the paired SeismoMatch scale: input acceleration g-to-m/s² conversion (9.80665) and dimensionless record scaling are distinct.

### Why results can differ despite matching global load
The same total applied gravity can coexist with different foundation DOF restraints, local reactions, load distribution, shell-to-beam transfer, end offsets, mass eccentricities, stiffness modifiers and drift. Before comparing LTH/NLTHA to ETABS, prove model identity and matched load cases/units; then compare node reactions, story shears, story drifts, roof displacement, modal periods and local element actions. **Do not equate linear CQC/MRSM nonconcurrent envelopes with signed simultaneous transient time-history responses.**

## GUI and result-export contract

- Analysis windows: physically scrollable log text and NBC notes (vertical/horizontal bars), copy-all action and user-triggered **local** ZIP export for either linear or nonlinear run. Existing analysis entry points and log paths remain intact.
- Completed history viewer: visible scroll-up/down controls and a canvas scrollbar so large result figures are accessible without resizing the screen. Preserve separate, labeled linear and nonlinear source files.
- Review ZIP: immutable snapshot of output-folder files under `Review_ZIPs/`; no original result relocation or source modification. `REVIEW_EVIDENCE_MANIFEST.json` records relative paths and SHA256; archives, EDB, credential extensions, symlinks and files above configured size limit are excluded. Missing inputs stay missing, never substituted with zeros. Ground motions located **outside** the selected run folder are not copied automatically.
- The archive may still contain personal Windows paths, geometry, filenames, source identifiers, imported records or other confidential thesis data inside JSON/logs. **Inspect and redact before sharing with anyone or posting publicly.** ZIP creation is not code acceptance or material calibration.
- Recommended long-term output organization: `<model>/<state>/{Gravity,ESM,Modal,MRSM,Linear_Time_History,Nonlinear_Time_History,Comparisons}/<run_id>/{Inputs,Logs,Analysis,Tables,Plots,Reports,Review_ZIPs}`. Existing source results must not be moved silently; migrate future writes only after caller/path tests and backward-compatible read lookup.

## Public-repository security review

### Checks added
`python tools/security_audit.py --repo .` enumerates **git-tracked files at current HEAD** and searches for common real credential prefixes, private-key headers and credential assignments. Only path, line number and finding category are printed; values are never echoed. Binary/oversized files are skipped and counted. CI compiles modified Python files, checks the review ZIP behavior and runs the scanner using minimal read-only GitHub Actions permissions; checkout does not persist credentials.

### Review and limitations
A preliminary GitHub code search for common OpenAI, GitHub, Google and AWS secret prefixes returned no indexed matches on 2026-11-11. This is **not a whole-repository historical or binary audit**. The scanner will miss obfuscated secrets, unknown providers, some environment variable access paths, Git LFS content and past commits. GitHub repository/security settings and hidden Actions secrets cannot be inspected through this review. No credential should be interpreted as safe merely because an indexed search returned zero.

Before publicly sharing ZIPs, review contents for ETABS/EDB proprietary data, sensitive floorplans, absolute usernames, passwords, email addresses, tokens, private calibration files, and licensed PDFs. Keep `.env`, certificates, access credentials, native source exports and full result ZIPs outside Git. Prefer restricted GitHub repository secrets and minimum-scoped short-lived tokens rather than plaintext configuration. Never print environment variables or tokens into logs.

**Recommended history scan from a trusted Windows terminal (run locally, never paste raw results publicly):**

    git fetch --all --prune
    gitleaks git --redact --report-format json --report-path security_history_private.json

Keep the report private. If a live secret is found: revoke/rotate the credential **immediately**, review cloud activity, remove it from HEAD, then coordinate Git history rewriting with all collaborators; merely deleting the current file does not remove historical exposure. Enable GitHub secret scanning / push protection if available for the repository. Check branch protections and dependencies separately. Avoid installing unverified automatic CI actions with write privileges.

### Acceptance gates not completed by this change
Windows Tk keyboard/trackpad scroll, Excel viewer integration, ETABS native response comparison, full-sequence linear and nonlinear histories, explicit FVD/wall fiber calibration, Windows-only solver behavior, latest origin/source workbook hashing, and historical secret scan. All require execution with the actual current Windows runtime and engineering data.

## Source changes
`components/ui/history_review_tools.py`, `components/ui/history_results.py`, `components/{linear_time_history,nonlinear_time_history}/runner_and_gui.py`, `tools/security_audit.py`, `tests/test_history_review_tools.py`, `.github/workflows/history-ui-security.yml`.

Original model EDBs and project calculations are not edited by these UI/tool changes.
