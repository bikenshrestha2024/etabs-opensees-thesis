# LITERATURE — thesis source library

**Catalogued 2026-11-12.** Primary literature for the asymmetric-plan 25-storey RC core, damped-outrigger and OpenSees NLTHA thesis.

## Folder layout and contents

- [MASTER_LITERATURE_INDEX.csv](MASTER_LITERATURE_INDEX.csv) — searchable bibliography; DOI, authors, journal, publication date, PDF availability, citation count and provenance.
- [CITATION_AND_PDF_POLICY.md](CITATION_AND_PDF_POLICY.md) — how citation counts and PDF permissions are recorded.
- [UPLOAD_INVENTORY.md](UPLOAD_INVENTORY.md) — the five papers uploaded in this conversation, exact metadata and SHA256 storage requirements.
- [TOPICAL_READING_GUIDE.md](TOPICAL_READING_GUIDE.md) — staged reading pathway for thesis modelling.
- [FREE_PDF_LINKS.md](FREE_PDF_LINKS.md) — verified open publisher landing pages and institutional source routes.
- **Private local PDF bundle:** user-supplied PDFs are kept out of the public GitHub repo pending explicit redistribution permission or confirmed public license. The included files remain available privately in the downloadable literature ZIP delivered in chat, not through GitHub.

## Rules

1. Use DOI as canonical identity; never invent missing DOI, date or citation count. Unknown entries are deliberately blank or marked pending.
2. Cite publication date separately from received/accepted dates. `2026-09-14 accepted` is NOT a claimed publication date.
3. `Citation_count` is a snapshot from an identified source, not a permanent numerical property and not a quality ranking. Do not mix Web of Science, Scopus, Google Scholar, Crossref, OpenAlex counts.
4. A user-uploaded PDF does NOT imply Creative Commons or permission to upload it to a public GitHub repository.
5. Record DOI, publisher URL, institutional author PDF if legally hosted, open-access license, checked-on date, checksum, applicable figures/tables, assumptions and transfer restrictions.
6. Papers for low- to medium-rise buildings or alternative dampers are background only; do not use them to validate the 25-storey asymmetric FVD model.
7. Do not mark a paper as `PROJECT_VERIFIED` simply because its parameter or formulation was imported.

## Maintenance

Add new works by unique DOI; preserve existing stable IDs. On each citation refresh store *source, UTC retrieval date, count, and methodology*. Keep the catalog useful offline: URLs are references; private PDFs must not be silently pushed. See [existing curated source registry](../docs/00_RESEARCH_REFERENCES.md) for R01–R13 linkage.

The curated master catalog includes 36 works. The automated source audit also detects additional DOIs and reports uncatalogued sources separately; a matched DOI alone does not mean full metadata has been verified. Incomplete bibliographic fields represent **outstanding verification**, not implied completeness.

## Classification folders

- [FVD](FVD/README.md) — Maxwell dampers, viscous dampers, damper placement, connections
- [BRB](BRB/README.md) — brace hysteresis, buckling restraint, fatigue
- [Shear Wall](Shear_Wall/README.md) — FSAM, SFI-MVLEM-3D, E-SFI, openings
- [Outrigger](Outrigger/README.md) — conventional, damped, belt/cap truss and position optimization
- [Reinforcing Steel](Reinforcing_Steel/README.md) — Steel02/SteelMPF, cyclic sensitivity, calibration
- [Concrete](Concrete/README.md) — Concrete01/02/CM, confinement and experiments
- [Ground Motions](Ground_Motions/README.md) — accelerograms, spectral matching, bidirectional histories
- [Codes and Standards](Codes_Standards/README.md) — NBC 105 and other standards
- [OpenSees Methods](OpenSees_Methods/README.md) — element formulation and numerical implementation
- [Material Calibration](Material_Calibration/README.md) — parameter uncertainty and benchmark reproduction

## Actual repository-source citation audit

- [Code citation occurrences](CODE_CITATION_OCCURRENCES.csv) — generated reference, category, source filename, **line number**, and matched curated ID where available
- [Uncatalogued DOIs](UNCATALOGUED_DOIS.csv) — source-discovered DOIs not yet matched to an individually verified master record; these require bibliographic review
- [Scan coverage](CODE_CITATION_SCAN_SCOPE.json) — actual counts, scope and exclusions
- [Offline scanner](tools/audit_source_citations.py) — run from Python 3.12 with no third-party dependencies
- [Automated workflow](../.github/workflows/literature-citation-audit.yml) — scans active tracked code/research text on relevant main-branch pushes; commits **only generated text indexes**, not PDFs

Each classification folder contains both the curated human-facing README and an automatically generated CODE_REFERENCES.md with code locations. This automated scan catches DOI/URL literal citations; full author-year references, incomplete/malformed DOI strings, inaccessible content and paper citations embedded only in figures still require manual review.

## Two new papers attached 2026-11-12

- **L029** Naseri, Amini and Kazemi (2024), DOI 10.1007/s41062-024-01574-7, is classified under FVD and Outrigger. Uploaded copy is an **author proof**, not verified final typeset journal version or a license for redistribution.
- **L030** Rouhani, Aghayari and Mousavi (2024), DOI 10.1016/j.engstruct.2024.118927, is classified under FVD. The uploaded tackle-damper PDF could not be parsed due to structural PDF errors; bibliographic identity is verified through publisher, but local PDF quality is flagged.

The uploaded papers remain in a **private chat ZIP**, not the public repository. See [upload inventory](UPLOAD_INVENTORY.md).

## Current audit summary (2026-11-12)

The GitHub Actions scanner completed an active-text scan of **844 tracked source files**, discovered **285 distinct DOI/URL strings** and generated **2,092 category-expanded source locations** without read errors. The original resulting list contained **44 unregistered DOI strings**; a subsequent six-source publisher-verification pass matched several of those, and later scan output is authoritative for remaining count. This is an **inventory**, not a complete bibliometric verification: plain author-year mentions are not captured unless accompanied by DOI/URL.

[Open GitHub Actions execution evidence](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/workflows/literature-citation-audit.yml).
