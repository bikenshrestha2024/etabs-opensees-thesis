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
