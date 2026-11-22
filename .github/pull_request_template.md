## MANDATORY READ-FIRST ENGINEERING PREFLIGHT

- [ ] Actually read `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md` and `.agents/skills/etabs-opensees-read-first/SKILL.md` **before edits** (do not check this box if only a tool automatically checked that the files exist).
- [ ] Physical topology remains **32 true foundation supports + 44 shear-wall mesh points**; no automatic 76/97 physical support substitution or severed mesh connectivity.
- [ ] Full gravity comparison remains **1.0D + 1.0L**, distinct from NBC 105:2025 **§5.2/Table 5-1** seismic-weight participation.
- [ ] Exact model EDB/source-workbook hashes, source case, wall geometry and module/reader effects documented, or marked **UNAVAILABLE**.
- [ ] Historic gross-shell 3041 kN and rebuilt elastic 768 kN residuals not conflated; no claim of native acceptance from total reaction balance.
- [ ] Structural changes have same-source independent native ETABS/OpenSees evidence; if not, engineering acceptance explicitly remains **NOT_VERIFIED**.

**Preflight paths actually read:** <paths or NOT_READ>  
**32+44 topology impact:** <PRESERVED / CHANGED_WITH_EVIDENCE / UNVERIFIED>  
**Gravity 1D+1L impact:** <PRESERVED / CHANGED_WITH_EVIDENCE / UNVERIFIED>  
**NBC Table 5-1 seismic-weight impact:** <PRESERVED / CHANGED_WITH_EVIDENCE / UNVERIFIED>  
**Native comparison gate:** <RUN with evidence / NOT_RUN>

## ROLE
Which engineering and code-review responsibilities apply?

## TASK
What was changed? Link the issue and exact affected files.

## FORMAT
| Verification | Result | Evidence |
|---|---|---|
| Unit tests | NOT RUN | command/log |
| Native OpenSees | NOT RUN | run ID/log |
| Source hashes | NOT RUN | manifest/report |
| NBC source clauses | REQUIRES REVIEW | source/section |
| Documentation (.py.md, JSON schema) | REQUIRES REVIEW | paths |

## CONSTRAINTS
- [ ] No original waveform or ETABS source modified or uploaded
- [ ] No double scaling of already matched Soil C records
- [ ] XY/YX and units preserved, current modal period requirements checked
- [ ] No unfinished trial reported as completed NLTHA
- [ ] Old versions remain archived and old entrypoint compatibility considered
- [ ] Changed Python modules have their own guide and deterministic test

## Engineer review / unresolved items
Explicitly describe failed tests, unknown material parameters, site Vs30, source selection and native solver limitations.
