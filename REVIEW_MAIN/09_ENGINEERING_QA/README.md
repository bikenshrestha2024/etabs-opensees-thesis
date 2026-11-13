# Engineering questions and answers — review index

**Project:** 25-storey asymmetric high-rise, ETABS-to-OpenSeesPy, NBC 105:2025. **Status:** living engineering decision register, not a compliance certificate. **Updated:** 2026-11-13.

The canonical `REVIEW_MAIN/00_MODEL`, `01_GRAVITY`, `05_LINEAR_TH`, `06_NONLINEAR_TH` and `07_TIME_HISTORY` issue records remain authoritative. The Q&A entries here explain assumptions and direct readers to those issues; they do **not** replace result logs or move any historical evidence.

## Categorized Q&A navigation

| Category | Question | Answer / authoritative record | Acceptance |
|---|---|---|---|
| [01_CODE_BASIS](01_CODE_BASIS/README.md) | Which code governs seismic analyses? When may IS 16700 be used? | NBC 105:2025 for seismic methods, combinations, demand and checks; IS 16700:2023 §7.2(d) for compulsory project initial EQ P-Delta cases; IS Table 5 conventional slab bending | **Adopted policy; amended IS text pending** |
| [02_PDELTA_INITIAL_STATES](02_PDELTA_INITIAL_STATES/README.md) | Why not retain ±1.5EL under every bidirectional record? What is tangent-stiffness versus full-state continuation? | [Detailed signed-EL versus gravity-equilibrium explanation](02_PDELTA_INITIAL_STATES/01_SIGNED_EL_VS_GRAVITY_START.md) | **Method reviewed, native state transfer open** |
| [03_GRAVITY_MASS](03_GRAVITY_MASS/README.md) | Is NBC §5.2 gravity the same as the full 1D+1L benchmark or IS initial P-Delta load combination? | Three purposes, independent load-pattern ledgers and support-reaction checks | **Source-load identity pending** |
| [04_ETABS_OPENSEES](04_ETABS_OPENSEES/README.md) | Can ETABS's initial-case tangent stiffness be directly copied into OpenSees NLTHA? | Static linearization and full nonlinear constitutive-history continuation are different; see source/test crosswalk | **Not certified** |
| [05_TIME_HISTORY](05_TIME_HISTORY/README.md) | What must be preserved when switching from gravity to ground motion? | Converged gravity, `loadConst`, `wipeAnalysis`, new excitation patterns, baseline reference, paired XY/YX | **Requires native end-to-end checks** |

## Every new question must contain

**Question; short answer; why; adopted source and exact clause (edition/amendment); when applicable; OpenSees/ETABS implication; evidence needed; status; owner; links to the canonical issue and provenance.** Never say “verified” merely because a command executed, a GUI showed green, or a code example compiled.

### Related canonical documents
- [P0 initial-case code hierarchy](../00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md)
- [P-Delta gravity handoff](../07_TIME_HISTORY/20261113_NBC_GRAVITY_PRELOAD_TO_EQ_TRANSIENT_DECISION.md)
- [Primary code and two IS exceptions](../../KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/NBC105_GOVERNING_CODE_MATRIX.md)
- [Thesis acceptance gates](../../docs/00_THESIS_ACCEPTANCE_GATES.md)

**Security:** never commit source EDB, private model workbooks, raw earthquake records, sensitive local paths, licensed standard PDF, watermarks, personal identity or unredacted exported case packages to the public repository.
