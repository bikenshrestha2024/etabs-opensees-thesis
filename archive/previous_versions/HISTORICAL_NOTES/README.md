# Historical notes by research subject

These are **immutable release-specific research reports**, not current program instructions, model calibration or evidence of successful native ETABS/OpenSees analysis. For active workflows start at [the current program index](../../../docs/programs/00_PROGRAM_INDEX.md), [engineering validation gates](../../../docs/00_THESIS_ACCEPTANCE_GATES.md), and [root README](../../../README.md).

All ten notes were moved without rewriting their original Git blob content. Old Git manifest paths remain historical; use the links below to retrieve the relocated files. No current launcher, engine module, source EDB or Excel workbook moved. Structural conclusions in the notes remain subject to current source/model verification.

## Diagnostic and modeling reviews
- [00_V163_NONLINEAR_DIAGNOSTIC.md](RESEARCH_DIAGNOSTICS/00_V163_NONLINEAR_DIAGNOSTIC.md)
- [00_V164_LOAD_AND_NONLINEAR_REVIEW.md](RESEARCH_DIAGNOSTICS/00_V164_LOAD_AND_NONLINEAR_REVIEW.md)
- [LITERATURE_REVIEW_AND_DECISION_V137.md](RESEARCH_DIAGNOSTICS/LITERATURE_REVIEW_AND_DECISION_V137.md)
- [REVIEW_V151.md](RESEARCH_DIAGNOSTICS/REVIEW_V151.md)

## Material and visualization research
- [MATERIAL_SETUP_V156.md](MATERIAL_RESEARCH/MATERIAL_SETUP_V156.md)
- [VISUAL_VALIDATION_V149.md](MATERIAL_RESEARCH/VISUAL_VALIDATION_V149.md)

## Release, hotfix and package history
- [CHANGES_AND_LIMITS_V138.md](RELEASE_CHANGELOGS/CHANGES_AND_LIMITS_V138.md)
- [00_V165_LAUNCHER_FIX.md](00_V165_LAUNCHER_FIX.md)
- [EXPORT_HOTFIX_V142.md](EXPORT_HOTFIX_V142.md)
- [PACKAGE_CONTENTS_V141.md](PACKAGE_CONTENTS_V141.md)

## Verification limits
Preservation is checked using the expected original Git **blob SHA** by [the archive test](../../../tests/test_historical_note_archive.py). This is not a Python import/Windows/Spyder regression nor physical model validation. Root count after this pass: 176 tracked files, 129 Python files remaining, 7 fewer tracked root files than the immediately preceding commit.
