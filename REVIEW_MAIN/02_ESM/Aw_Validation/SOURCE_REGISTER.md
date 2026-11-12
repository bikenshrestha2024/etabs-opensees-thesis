# Reference sources — traceable bibliography

| ID | Authors/agency, year | Title | Where to look | DOI / primary link | Use |
|---|---|---|---|---|---|
| N01 | Government of Nepal / DUDBC, 2025 | NBC 105:2025 Seismic Design of Buildings in Nepal | §5.1.2 pp.29–30; §5.1.3; §5.5; §5.6 | https://dudbc.gov.np/pages/24231978/ | Governing; not attached as a PDF in 2026-11-12 batch |
| R01 | Structural Engineers Association of California, published 2000 | 1997 UBC Seismic Design Manual, Vol I, Example 19 | Uploaded combined Vol I–II PDF, **PDF p.66**, printed p.63 | No DOI | Masonry worked example: De=60ft; net opening Ae=12.7ft²; historic opening method |
| R02 | SEAOC Seismology Committee, 2019 | SEAOC Blue Book, Seismic Design Recommendations 2019 | Article 04.03.010, Period Determination, **PDF p.125**, Article p.4/9 | https://www.seaoc.org/page/bluebook | Explicit RC/masonry applicability; min horizontal area vs full wall length |
| R03 | SEAOC, examples principally Joseph R. Maffei, 2000 | SEAOC Seismic Design Manual Vol III, Steel Concrete and Cladding | RC wall Example 4 printed p.209; coupled RC wall Example 5 printed p.237+; screenshot PDF p.250 | No DOI | RC physical coupling and wall-opening modeled response, NOT direct Aw arithmetic |
| R04 | Can Balkaya & Erol Kalkan, 2004 | Seismic vulnerability, behavior and design of tunnel form building structures | Engineering Structures 26:2081–2099; **printed p.2086 Eq.3** | https://doi.org/10.1016/j.engstruct.2004.07.005 | RC-specific code formula; FEM/period accuracy warning |
| R05 | Rakesh K. Goel & Anil K. Chopra, 1998 | Period Formulas for Concrete Shear Wall Buildings | ASCE J. Structural Engineering 124(4):426–433 | https://doi.org/10.1061/(ASCE)0733-9445(1998)124:4(426) | Direct RC period research; code period empirical uncertainty |
| R06 | International Conference of Building Officials, 1997 | 1997 Uniform Building Code **Volume 1** | User upload background only | https://www.najah.edu/media/cms_page_media/482/UBC_Volume2.pdf | Structural §§1628/1630 are in **Volume 2**; do not miscite Vol 1 as Volume 2 |

Source PDFs were supplied by the user for private review. Public repository contains bibliographic metadata **only**, no copyrighted source PDFs. Source SHA256 and exact original filenames are included in the separately provided research ZIP's `07_SOURCE_PROVENANCE/REFERENCE_REGISTER.csv`. Duplicate Balkaya paper upload was not stored twice.

## Claim-to-reference mapping
- **Governing formula / 1.25 amplifier:** N01.
- **Minimum net first-storey horizontal concrete area:** N01 (effective area, not explicitly opening method), R01/R02 (historical definition).
- **Full wall length despite multiple openings:** R01 worked example; R02 definition.
- **Formula applies to RC shear wall building:** R02, R04, R05.
- **Wall-pier coupling and spandrel design:** R03 and NBC 105 §§5.5–5.6, not an alternative empirical period formula.
- **Period may depart from empirical prediction:** R04/R05.
- **Two 12m X wall lines:** current ETABS user-supplied **screenshots only**, native first-storey EDB inspection outstanding.

## Additional uploaded RC research — 12 November 2026

See [20261112_ADDITIONAL_RC_SOURCES_REVIEW.md](20261112_ADDITIONAL_RC_SOURCES_REVIEW.md) for the detailed register of Lee, Chang & Chun (2000); Fares (2018); SEAOC Blue Book (1999); Hsiao (2014); Kim & Lee (2003); and Daniel, Shiu & Corley (1986), together with applicability limits and previously known duplicate editions. All source PDFs remain outside this public repository; the private manifest records full SHA256 and PDF pages. **No change to the selected two-12m X-wall Aw calculation.**
