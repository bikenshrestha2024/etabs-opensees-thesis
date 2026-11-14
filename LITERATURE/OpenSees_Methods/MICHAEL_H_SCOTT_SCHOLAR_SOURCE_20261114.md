# Michael H. Scott — Google Scholar profile and OpenSees methods source

**Registered:** 2026-11-14  
**Evidence type:** researcher profile / discovery resource, **not** an individual peer-reviewed work or project calibration record  
**Google Scholar:** https://scholar.google.com/citations?user=jwa3XqcAAAAJ&hl=en  
**Attribution verification:** an Oregon State University hosted CV explicitly prints `scholar.google.com/citations?user=jwa3XqcAAAAJ` alongside Michael H. Scott's name: https://resilience.colostate.edu/files/bios/MHS_NIST_resume.pdf . His university-hosted publication list corroborates name and structural-engineering affiliation: https://web.engr.oregonstate.edu/~mhscott/ . His OpenSees developer website: https://openseesdigital.com/about/ .

## Engineering purpose
Michael H. Scott's published work and OpenSees development resources are particularly useful to the project's **numerical methods and implementation** (force-based beam-column elements, plastic-hinge formulations, integration, nonlinear algorithms, OpenSees software architecture and response sensitivity). Researcher-profile existence does **not** qualify the full ETABS-to-OpenSees converter or project-specific numerical model.

## Suggested primary works for independent source verification
1. McKenna, F., Scott, M.H. & Fenves, G.L. (2010), *Nonlinear finite-element analysis software architecture using object composition*, Journal of Computing in Civil Engineering **24**(1), 95–107. Verify publisher DOI and bibliographic metadata before adding a master-index entry.
2. Scott, M.H. & Fenves, G.L. (2010), *Krylov subspace accelerated Newton algorithm: Application to dynamic progressive collapse simulation of frames*, Journal of Structural Engineering **136**(5), 473–480. Verify actual applicability to a nonlinear earthquake history and convergence evidence before changing any solver.
3. Scott, M.H. & Ryan, K.L. (2013), *Moment-rotation behavior of force-based plastic hinge elements*, Earthquake Spectra **29**(2), 597–607. Suitable for review of nonlinear frame hinge assumptions after obtaining project reinforcement.
4. Scott, M.H. & Haukaas, T. (2008), *Software framework for parameter updating and finite element response sensitivity analysis*, Journal of Computing in Civil Engineering **22**(5), 281–291. Author-hosted article: https://web.engr.oregonstate.edu/~mhscott/Scott-Haukaas_JCCE_2008.pdf .
5. Simpson, B.G., Zhu, M., Seki, A. & Scott, M.H. (2023), *Challenges in GPU-accelerated nonlinear dynamic analysis of structural systems*, Journal of Structural Engineering **149**(3). Useful as background for profiling and solver performance, not a recommendation to enable GPUs blindly.

Publication titles, year and venue are listed on the author's university-hosted page. **DOIs, citation counts, full-text licenses, test specimens and model transfer permissions must be independently verified for each individual work.** Do not convert old Scholar citation counts into current counts.

## Repository decision
- Preserve existing `LITERATURE/MASTER_LITERATURE_INDEX.csv` stable IDs and DOI-as-identity convention. This is a source-directory record, not a newly verified paper DOI.
- Keep OpenSees command syntax sourced to the official documentation: https://opensees.github.io/OpenSeesDocumentation/ .
- Keep this as `REFERENCE_ONLY`. No automatic changes to `components/model/assembly.py`, `components/gravity/`, `components/nonlinear_time_history/`, numerical controls, model forces or acceptance gates.
- Any eventual code change requires a small independent reproducible benchmark and source-specific documented justification (including full-source citation, version, adopted assumptions, unit system, and exact differences from the user's model).
- No publication PDFs have been added or republished by this commit. 
