# Publication and navigation decisions — 2026-11-10

Authorization: the user explicitly requested that all current changes be
committed to main, the supplied Excel files also be included on main, all
Excel workbooks be organized under a folder named `excel`, and the main
launcher be named `01` with the run order arranged accordingly. This supersedes
the earlier instruction to leave the implementation as an unmerged draft PR.
It does not authorize inventing structural equivalence or changing originals.

| Decision | Implementation | Reason / evidence |
|---|---|---|
| Publish completed implementation to main | Merge the tested PR #17 with its final head checked | Explicit current user instruction; preserve branch/commit history |
| Main launcher named 01 | Root `01.py`; old launchers remain compatibility delegates | Requested name without breaking existing launch references |
| Clean numbered navigation | `launchers/README.md`, program index and canonical audit agree | Existing numeric IDs remain stable; historical aliases are not an alternate work order |
| One workbook directory | 68 workbooks under `excel/` | 63 tracked workbooks moved byte-for-byte; three supplied source workbooks and two new verification reports added |
| Preserve calculator source | Existing supplied calculator was already byte-identical to the tracked one | Move it once rather than create another active copy |
| Retain historical evidence | `excel/historical/` keeps the former relative hierarchy | Preserve every SHA256; frozen scientific review ledgers remain historical records |
| Historical execution compatibility | Read-only restore plan and optional `--restore` tool | Never overwrite a different old output; new active code uses excel directly |
| Large full-table workbook | Git LFS, original 530969448 bytes | Ordinary GitHub files are limited to 100 MiB; do not trim tables or recompress the workbook |
| Portable defaults | Relative source registry, exact EDB SHA and workbook SHA | Avoid machine-specific public paths and cross-model automatic selection |
| Exported runtime inputs | Copy only established small calculator/scaling inputs; retain verified references to larger sources | Do not copy the full-table workbook into every runtime export |

## Source and evidence contents

`excel/source/` includes the original assignment workbook, full ULS ETABS
export, original NBC calculator, existing ULS/SLS scaling workbooks, and the
supplied verified-clear-beam slab load-path formulas. Original external files
remain untouched. `excel/verification/20261110_primary32/` contains the gravity
report and offline native ETABS reaction-comparison workbook produced by the
isolated instrumented run. Their generating code commit is recorded in the
catalog, independently of the later publication commit.

The verification workbooks are research evidence, not adopted design inputs.
The source registry therefore does not map either report to a calculator role.
No EDB, accelerogram, private machine registry or chat attachment is published
by this change. The user's instruction explicitly authorizes these workbooks.

## Preserved engineering decisions

- 32 reaction-bearing nodes remain the main gravity case; 76 and 97 are saved
  sensitivity alternatives. Old internal identifiers remain for compatibility.
- Original adopted design periods are X=2.03856740011866 s and
  Y=1.9219797767063125 s. Modal and static Rayleigh periods remain independent.
- The native instrumented 32-node rerun reproduced all saved displacements
  and support Fz exactly, with 11097 joint equilibrium residuals below 4e-10 kN.
- Individual ETABS reactions remain different: joints 263/264 differ by
  3041.265778 kN (20.6208%). The 44 other base source points have no exported
  frame/shell end-force rows for this gravity combination; this is a native
  topology/coverage finding, not proof of a free physical DOF. End-zone stiffness
  and internal native mesh correspondence still require reconciliation.
- No geometry, load, mass, material, solver equation or support definition
  was changed for publication. Moving workbooks does not resolve the documented
  nonlinear first-step failure, seismic acceptance or local-reaction mismatch.

## Reproduction and rollback

Clone with Git LFS, run `git lfs pull`, then `python 01.py`. Review
`excel/WORKBOOK_CATALOG.json` for byte identities and former paths. Run the
compatibility restore tool only when reproducing an older snapshot. The
publication commit and migration catalog permit reversal without editing
workbook contents or rewriting Git history.

Validation includes the existing gravity/ESM/MRSM regressions, the new workbook
hash/location and restore tests, launcher/navigation checks, public reference
tags, and GitHub CI. Native solver evidence belongs to the earlier recorded
run; no new native ETABS solve is implied by publishing these files.

Sources: [GitHub ordinary-file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github),
[Git LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage).

Executed before publication: **214 tests and 5 subtests passed**, plus all
four reference-tag checks. Static inventory found 419 active modules with
no syntax errors, missing canonical launchers or missing source guides.
Git LFS fsck passed. The hash catalog checks every workbook, including the
LFS object identity when CI has a pointer-only checkout.
