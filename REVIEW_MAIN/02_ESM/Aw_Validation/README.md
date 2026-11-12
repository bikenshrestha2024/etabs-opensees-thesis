# Aw Validation — 2026-11-12

**Status:** PREFERRED INTERPRETATION / NOT YET EDB VERIFIED.

This text-only public review folder accompanies a **separate private ZIP of the user-supplied PDFs**. Do NOT commit those source PDFs, original EDB, original Excel, or internal paths to this public repository.

## Directional effective area, NBC 105:2025 §5.1.2

Assume seismic wall height H=95m and thickness t=0.6m, to be verified from the selected original EDB:

| Case | Wall grouping | Minimum net horizontal area per wall | Whole-wall Lwi | Aw total (m²) | Status |
|---|---|---:|---:|---:|---|
| X old | Four independent 6m panels, 1 x 2m door each | 2.4m² | 6m | 1.958293629 | Alternative if actual wall separations |
| **X candidate** | **Two parallel 12m continuous RC wall lines**, 2 x 2m doors each | **4.8m²** | **12m** | **2.073174515** | **Preferred; inspect native EDB** |
| X 24m | One fictitious straight 24m wall | 9.6m² | 24m | 2.532698061 | DO NOT ADOPT without one actual collinear wall |
| Y unchanged | Three 6m solid Y walls | 3.6m² | 6m | 2.203080332 | Verify original 3 wall identities |

Formula **sum PER wall** `Awi*[0.2+(min(Lwi/H,0.9))²]` — **never** sum independent factors or `(Lwi/H)` terms as a replacement. Structural wall length does **not** reset at an architectural 6m grid or ETABS area mesh-object division when reinforced-concrete continuity is physically present.

## Engineering judgment
User screenshot X elevations at core wall lines 3 and 4 show uninterrupted structural wall elevation spanning two 6m bays with circulation door perforations and spandrel concrete; the plan shows two separated, parallel X wall lines. This favors each 12m line as ONE structural wall, subject to source geometric/section verification. **Two parallel wall lines are not a single straight 24m wall** merely because they are connected by perpendicular walls or a diaphragm.

First-storey `Awi` is the **minimum horizontal net concrete section** through the openings. Confirm whether both 2m door openings overlap the same 2.3m-tall vertical slice; otherwise do not assume the net area is 4.8m² at the critical section. Spandrels above the doors do NOT count twice as extra area but must be modeled for coupling and strength.

UBC 1997 §1628 and §1630.2.2 supply historical wall-length/area definitions. SEAOC Vol I Example 19 (1997 UBC) demonstrates 60ft whole-wall length with four openings; its example is **masonry**. SEAOC Blue Book 2019 Article 04.03.010 and Balkaya & Kalkan (2004) explicitly establish relevance of the formula to **reinforced concrete**. Goel & Chopra (1998) caution empirical periods may not match actual periods. Not an official Nepal NBC 105 door-specific commentary.

## Sources and evidence
See [Source register](SOURCE_REGISTER.md) and [Acceptance checklist](REVIEW_GATES.md). Store locally in a research evidence directory; don't upload copyrighted PDFs. The complete offline reference bundle is user-specific.

## Source authority
Original NBC 105:2025 §5.1.2 controls, including definition of H and §5.1.3 1.25 factor. No original NBC PDF was in the new uploads; original code URL: https://dudbc.gov.np/pages/24231978/

**Do not silently modify original Excel Aw or adopt code acceptance solely from screenshots**. The previously source-verified workbook and current EDB identity must be reconciled first; the continuous-pier OpenSees output is a separate diagnostic.
