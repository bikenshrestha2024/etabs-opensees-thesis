# Root-clutter audit and compatibility-first cleanup — 2026-11-15

**Status: static inventory and safe preflight only; no mass file relocation or native solver validation.**

## Verified live Git tree baseline
- Branch: `main`; baseline commit: `4023d4e41e18dc8cc668a4cc0fa8b7d88c4b9e04`.
- 3,010 tracked blobs in a non-truncated recursive Git tree; 186 tracked root files (129 Python, 33 Markdown, 19 JSON, 2 CSV, 1 log, 2 Git metadata).
- Large historical/project areas include `docs/`, `Saved_Project_V156/`, `Worked_Example_V132/`, `components/`, `tests/`, and `REVIEW_MAIN/`.
- Root prefix collisions are real: `01_WORKFLOW_START.py` and `01_START_ETABS_TO_OPENSEES.py`; `17_BUILDING_FULL_NONLINEAR.py` and `17_LITERATURE_COMPONENT_DEMO.py`. Prefixes are **IDs, not run order**.
- The root already has legacy archives and organized `01_ETABS` through `07_REVIEW_MAIN` navigation. Creating another parallel source tree would increase ambiguity.

## Immediate changes
1. Make README navigation consistent and distinguish `01_WORKFLOW_START.py` (canonical) from `01.py` (compatibility entry).
2. Add `tools/audit_repository_layout.py` to identify tracked-root file classifications, duplicate launcher prefixes and exact-name reference blockers **without moving anything**.
3. Preserve source module paths and all historical files. Output audit is locally generated and untracked unless separately reviewed for privacy.
4. Keep source ETABS case output contract from `REVIEW_MAIN/08_SOFTWARE_SECURITY/20261114_CANONICAL_STAGE_FOLDER_AND_MIGRATION_AUDIT.md` authoritative; do not imply its target taxonomy is already implemented for all stages.

## Use
```powershell
python tools/audit_repository_layout.py --output audit/repository_layout.json
python -m unittest discover -s tests -p "test_repository_layout.py"
python tools/audit_active_repository.py --output audit/active_inventory.json --fail-on-missing-canonical
```

## Staged relocation plan (NOT performed)
- **Phase A, no relocation:** index and classify all root files; identify direct references, syntax and launcher compatibility.
- **Phase B:** for each historical report, search indirect constructed paths, Markdown links, GUI and tests; verify consumers, content SHA and provenance. Move only an individually approved, unconsumed artifact to `archive/previous_versions/<family>/`, update every reference in the same commit.
- **Phase C:** keep thin numbered Spyder compatibility launchers at root; move implementations only with complete import/caller graph and regression evidence. Do not move `components/` opportunistically.
- **Phase D:** update each analysis writer/reader pair to the case-owned `RUNS/<stage>/<case>` directory contract. Use atomic staging, run manifest, complete logs, comparisons, figures, missing-item registry and ZIP. Preserve legacy read paths until native tests pass.
- **Phase E:** only after Windows native regression, remove approved aliases and track actual count reductions.

## Engineering issues remain open
The X-wall first-step nonlinear failure, qualified RCC material/rebar mappings, 32/76/97-support semantics, gravity source reactions, shell/slab/wall transfer, period/ESM/MRSM equivalence, actual full-record XY/YX and M0–M6 outputs require independent project evidence. Static layout checks cannot certify any of them. Do not silently substitute assumed results or mark validation gates passed.

## Scope and provenance
Editor: ChatGPT (OpenAI GPT-6), GitHub connector. Static Git tree and repository policy inspected; the shared ChatGPT conversation URL was not retrievable. No local checkout, native ETABS, Windows/Spyder, OpenSees, or full semantic file-by-file review was available in this connector-only pass.
