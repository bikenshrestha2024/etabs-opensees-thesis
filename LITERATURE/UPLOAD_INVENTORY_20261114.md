# 2026-11-14 user-uploaded PDF intake — private evidence inventory

**Purpose:** catalogue the actual 19 PDF filenames attached to the 2026-11-14 discussion, identify the original works, avoid duplicate bibliography records, and link them to the five unresolved ETABS/OpenSees engineering issues and current modal results.

**Data protection:** This is *metadata only*. The user's PDFs were supplied in a private chat; public GitHub redistributions are **NOT authorized**, even where a public copy can be found online. Store originals locally, privately, with a calculated SHA256 before referencing them as a specific byte-identical copy. Do not commit PDFs or confidential ETABS/Excel datasets to this public repository.

**Verification labels:** `SOURCE_HEADER_READ` = metadata confirmed from the uploaded PDF's rendered or parsed opening pages; `PUBLISHER_CHECKED` = publication metadata additionally checked against publisher; `PROVISIONAL` = title/venue/DOI require confirmation; `BYTE_DEDUPE_PENDING` = likely same paper but original file hashes not available in the GitHub environment. None of these labels is a model validation claim.

## Intake: 19 PDF attachments (one row per uploaded file)

| No. | Uploaded file name | Canonical work | Primary class | Verification / duplicate relationship |
|---:|---|---|---|---|
| 01 | `The FAIR Guiding Principles for scientific data management and stewardship.pdf` | U01 Wilkinson et al. 2016 | FAIR/provenance | SOURCE_HEADER_READ |
| 02 | `VandV2024-25.pdf` | U02 Nobile 2025 | Verification and validation | SOURCE_HEADER_READ; slides about CFD/CHT, not a structural code |
| 03 | `FSI05011FU.pdf` | U03 Schwer 2005 | Verification and validation | SOURCE_HEADER_READ, PUBLISHER_CHECKED |
| 04 | `carlos_garcia_-_poster_-_peer_2019_-_final.pdf` | U04 García & Rea, PEER 2019 poster | ETABS/OpenSees workflow | SOURCE_HEADER_READ; poster, not peer-reviewed validation paper |
| 05 | `bathe1985.pdf` | U05 Bathe & Dvorkin 1985 | Shell / plate element | SOURCE_HEADER_READ |
| 06 | `2021-Optimaloutriggerlocationsanddampingparametersforsingle-outriggersystemsconsideringearthquakeandwindexcitations_4.pdf` | U06 Xing et al. 2021 (verify author list on title page) | Outriggers/FVD/BRB | SOURCE_HEADER_READ partial; PUBLISHER_CHECKED DOI |
| 07 | `Advances in Civil Engineering - 2020 - Alhaddad - Outrigger and Belt‐Truss System Design for High‐Rise Buildings  A.pdf` | U07 Alhaddad et al. 2020 | Outrigger/belt truss | SOURCE_HEADER_READ |
| 08 | `kolozvari2018_3.pdf` | U08 Kolozvari, Orakcal & Wallace 2018 | RC wall nonlinear materials | SOURCE_HEADER_READ, PUBLISHER_CHECKED |
| 09 | `an-overview-ot-he-asme-guide-for-verification-and-validation-in-computational-solid-mechanics_compress.pdf` | U09 Schwer 2006 | Verification and validation | SOURCE_HEADER_READ; overview, not official ASME standard |
| 10 | `kolozvari2018_2.pdf` | U08 Kolozvari, Orakcal & Wallace 2018 | RC wall nonlinear materials | SOURCE_HEADER_READ; BYTE_DEDUPE_PENDING against #08 |
| 11 | `charney2008.pdf` | U10 Charney 2008 | Nonlinear damping | SOURCE_HEADER_READ |
| 12 | `tbi-working-group-led-by-co-chairs-ron-ha-burger-and-jack-moehle_10.9.17_withlinks.pdf` | U11 PEER TBI 2017/06 v2.03 | Tall-building NLTHA | SOURCE_HEADER_READ |
| 13 | `tbi-working-group-led-by-co-chairs-ron-hamburger-and-jack-moehle_10.9.2017.pdf` | U11 PEER TBI 2017/06 v2.03 | Tall-building NLTHA | SOURCE_HEADER_READ; BYTE_DEDUPE_PENDING against #12 |
| 14 | `webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace_3.pdf` | U12 Kolozvari, Orakcal & Wallace 2015 | Wall cyclic benchmarks | SOURCE_HEADER_READ |
| 15 | `VandV2024-25(1).pdf` | U02 Nobile 2025 | Verification and validation | SOURCE_HEADER_READ; BYTE_DEDUPE_PENDING against #02 |
| 16 | `FSI05011FU(1).pdf` | U03 Schwer 2005 | Verification and validation | SOURCE_HEADER_READ; BYTE_DEDUPE_PENDING against #03 |
| 17 | `The FAIR Guiding Principles for scientific data management and stewardship(1).pdf` | U01 Wilkinson et al. 2016 | FAIR/provenance | SOURCE_HEADER_READ; BYTE_DEDUPE_PENDING against #01 |
| 18 | `1-s2.0-S2352710221008044-main.pdf` | U13 Kolozvari et al. 2021 | Nonplanar RC walls | SOURCE_HEADER_READ |
| 19 | `1-s2.0-S014102962301115X-main (3).pdf` | U14 Kolozvari, López & Massone 2023 | E-SFI-MVLEM-3D | SOURCE_HEADER_READ |

**Count:** 19 uploaded files, **14 distinct works by bibliographic identity** (pending byte-hash checks). Never silently delete the duplicate uploads; retain raw originals and select one canonical local copy only after SHA256 calculation and page count/edition comparison.

## Canonical verified bibliography (one row per distinct work)

| ID | Author, year, title | Venue / report | DOI or persistent URL | Relevant evidence and limits |
|---|---|---|---|---|
| U01 | Wilkinson, M.D. et al. (2016), *The FAIR Guiding Principles for scientific data management and stewardship* | Scientific Data 3, 160018, 15 Mar 2016 | https://doi.org/10.1038/sdata.2016.18 | Metadata and workflows; not seismic calibration |
| U02 | Nobile, Enrico (2025), *Verification and Validation (V&V)* | University of Trieste teaching slides, 27 Feb 2025 | DOI not provided in uploaded slides | CFD/CHT introduction; background V&V only |
| U03 | Schwer, L.E. (2005), *Verification and validation in computational solid mechanics and the ASME Standards Committee* | WIT Transactions on The Built Environment 84 | https://doi.org/10.2495/FSI050111 | General V&V process; NOT ASME V&V 10 text |
| U04 | García, Carlos & Rea, Nathanael (2019), *CEO: Convert ETABS to OpenSees — A Tool for Nonlinear Analysis of Reinforced Concrete Structures Subjected to Earthquakes* | PEER 2019 poster; advisor Kristijan Kolozvari | DOI not supplied | Converter architecture concept with material Excel, gravity, dynamic and recorder stages; not independently peer-reviewed or source-model equivalent |
| U05 | Bathe, K.-J. & Dvorkin, E.N. (1985), *A Four-Node Plate Bending Element Based on Mindlin/Reissner Plate Theory and a Mixed Interpolation* | IJNME 21, 367–383 | https://doi.org/10.1002/nme.1620210213 | Mixed-interpolation plate bending benchmark; not exact proof current OpenSees ShellMITC4/ETABS parity |
| U06 | Xing et al. (2021), *Optimal outrigger locations and damping parameters for single-outrigger systems considering earthquake and wind excitations* | Engineering Structures 245, 112868, 15 Oct 2021 | https://doi.org/10.1016/j.engstruct.2021.112868 | Single OR1/OVD1/OBRB1 simplified optimization; M0–M6 multi-outrigger transfer remains limited |
| U07 | Alhaddad, W.; Halabi, Y.; Xu, H.; Lei, H. (2020), *Outrigger and Belt-Truss System Design for High-Rise Buildings: A Comprehensive Review Part II—Guideline for Optimum Topology and Size Design* | Advances in Civil Engineering 2020, 2589735, published 21 Feb 2020 | https://doi.org/10.1155/2020/2589735 | Belt/outtrigger topology and size comparison; not evidence brace hinge is physically exact |
| U08 | Kolozvari, K.; Orakcal, K.; Wallace, J.W. (2018), *New OpenSees Models for Simulating Nonlinear Flexural and Coupled Shear-Flexural Behavior of RC Walls and Columns* | Computers & Structures 196, 246–262, Feb 2018 | https://doi.org/10.1016/j.compstruc.2017.10.010 | MVLEM, SFI-MVLEM, FSAM, ConcreteCM, SteelMPF with specimen benchmarking; material card requires project-specific calibration |
| U09 | Schwer, L.E. (2006), *An Overview of the ASME Guide for Verification and Validation in Computational Solid Mechanics* | 5th LS-DYNA Anwenderforum, Ulm, keynote paper | https://lsdyna.ansys.com/wp-content/uploads/2025/02/an-overview-of-the-asme-guide-for-verification-and.pdf | Overview of 2006 guide; **not** ASME V&V 10-2019 (R2025) standard itself |
| U10 | Charney, F.A. (2008), *Unintended Consequences of Modeling Damping in Structures* | Journal of Structural Engineering 134(4), 581–592 | https://doi.org/10.1061/(ASCE)0733-9445(2008)134:4(581) | Artificial forces in Rayleigh stiffness damping after yielding; consider when FVD and nonlinear RC are combined |
| U11 | PEER Tall Buildings Initiative (2017), *Guidelines for Performance-Based Seismic Design of Tall Buildings*, version 2.03 | PEER Report 2017/06, May 2017 | https://peer.berkeley.edu/publications/2017-06 | Tall-building PBSD criteria and nonlinear modelling, SUPPLEMENTARY_NOT_NBC; both uploads say v2.03 |
| U12 | Kolozvari, K.; Orakcal, K.; Wallace, J.W. (2015), *Shear-Flexure Interaction Modeling for Reinforced Concrete Structural Walls and Columns under Reversed Cyclic Loading* | PEER Report 2015/12, Dec 2015 | https://peer.berkeley.edu/publications/2015-12 | FSAM/MVLEM calibration and cyclic test reproduction |
| U13 | Kolozvari, K.; Kalbasi, K.; Orakcal, K.; Wallace, J.W. (2021), *Three-Dimensional Shear-Flexure Interaction Model for Analysis of Non-Planar Reinforced Concrete Walls* | Journal of Building Engineering 44, 102946 | https://doi.org/10.1016/j.jobe.2021.102946 | Four U-shaped wall experiments under multidirectional loads; shear lag/diagonal loading limitation stated by authors |
| U14 | Kolozvari, K.; López, C.N.; Massone, L.M. (2023), *Efficient Three-Dimensional Shear-Flexure Interaction Model for Reinforced Concrete Walls* | Engineering Structures 294, 116700 | https://doi.org/10.1016/j.engstruct.2023.116700 | Published E-SFI-MVLEM-3D with wall specimen benchmarks; reported reduced DOFs and improved numerical performance relative to parent element, NOT proven for current wall mesh |

## Explicit bibliographic distinctions and correction of earlier assumptions
- The `kolozvari2018_2` and `_3` papers are **2018** published journal work even though their uploaded preprint first page says accepted **17 October 2017**.
- The U13 (2021) `SFI-MVLEM-3D` is not identical to U14 (2023) **E-SFI-MVLEM-3D**; record exact OpenSees element constructor/version and panel modelling differences.
- García & Rea's PEER 2019 poster demonstrates a proposed GUI/workflow architecture, but does **not** establish direct physical equivalence for the user's multi-storey ETABS model.
- U02 Nobile covers CFD/CHT; do not label it experimental structural calibration.
- U09 is a summary of the historical ASME guide, not the authenticated current ASME standard.
- PEER TBI is supplemental performance-based guidance; NBC 105:2025 remains governing for this Nepal project.
- Missing current citation counts: **NOT RETRIEVED**. Counts are database-dependent and must not be fabricated.
- PDF SHA256 and page-count-difference verification: **PENDING LOCAL HASH AUDIT** (the attached bytes were not hashed in this GitHub change).

## Public/private storage decision
Public: this index, verified DOI and publisher links, source-to-thesis crosswalk, scripts that hash/local-index private files, reviewed citation statements.
Private: all 19 originally attached PDFs (even if a journal has an openly accessible copy, redistribution and public repo permissions must be checked independently), proprietary ETABS EDB and Excel tables, project-specific or unpublished specimen data.
