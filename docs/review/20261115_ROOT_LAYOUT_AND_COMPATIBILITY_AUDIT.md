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

## Second review: audit safety and CI checks (2026-11-15)
- Refuse symlinked tracked text inputs; a malicious symbolic link may otherwise cause local files outside the repository to be read during navigation audits.
- Skip malformed UTF-8 instead of replacing invalid bytes and reporting a misleadingly complete scan.
- Report skipped text-file count and block all automatic relocation candidates when scanning is incomplete.
- CI now executes the layout inventory regression tests and produces the layout JSON as a downloadable CI artifact (not a tracked source file).
- `/audit/` is ignored in local working trees. Confirm separately that sensitive evidence is not already present in Git history; ignoring future writes does not rewrite history.
- Static search findings are **not** a license to relocate root scripts: existing source/launcher references must be checked against actual Windows execution and test evidence.


## Targeted root reduction — 2026-11-15

Three historical, documentation-only V141/V142/V165 notes were moved to `archive/previous_versions/HISTORICAL_NOTES/`. Original Git blob SHAs are preserved; their former root paths are removed from the current tree. Current tracked root-file count decreases from **186 to 183**. Original contents, numeric models, launchers and source runtime paths are unchanged. See `archive/previous_versions/README.md` and `tests/test_historical_note_archive.py`.

**Reference caveat:** `MANIFEST_V167.json` and older release manifests retain historical filenames verbatim. Those archival manifests are provenance records, not runtime file-location instructions. Do not rewrite them to fabricate a new historical package layout. Any external links to the old root note URLs may require updating separately. No broad relocation is approved based on this narrowly scoped success.


## Third pass: seven source-preserving research note relocations (2026-11-15)

Seven additional V137–V164 documentation-only reports were moved into `archive/previous_versions/HISTORICAL_NOTES/{RESEARCH_DIAGNOSTICS,RELEASE_CHANGELOGS,MATERIAL_RESEARCH}/` without modifying any original Git blobs. Across both migrations: **10 root notes archived**, root tracked file count **186 → 176**, root Python scripts **129 unchanged**. This remains a partial root cleanup and does not certify full per-line semantics. The new archive index and regression test protect historical retrieval and byte identity. Exact-string GitHub search showed zero active `.py` references for these seven candidates; historical manifests, literature link text and curated source citations may still retain former root references. Archive records are not silently rewritten.

### Current priority defects (not fixed by reorganizing notes)
- Numbered launcher aliases collide (e.g. 01/17/20); sorting filenames cannot define the engineering run sequence.
- Native 32/76/97 support and gravity reactions remain unresolved equivalence questions.
- Production nonlinear first X-wall step fails; material/rebar/wall opening and FVD qualification remain engineering blockers.
- The target folder-per-stage specification is not yet universal writer behavior; changing root notes does not modify run outputs.
- Public repository visibility warrants an independent history/secret and sensitive evidence audit; these archive moves do not rewrite history.
