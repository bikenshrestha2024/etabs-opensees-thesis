# ETABS–OpenSees gravity load path: software-manual reference register

**Purpose:** centralize *official manuals* used to verify objects versus analysis mesh, shell/beam/wall gravity load transmission, rigid end offsets, restraint and multi-point constraint behavior and OpenSees reactions. These materials are documentation, NOT an experimental structural validation paper. No DOI or scholarly citation count is applicable.

| ID | Author / publisher | Document | Date / version | Official URL | PDF access | Use and limitation |
|---|---|---|---|---|---|---|
| G-M01 | Computers & Structures, Inc. | CSI Analysis Reference Manual (ETABS), Ch. IV, V, VII, X | July 2016 | https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf | Official PDF public-readable; redistribution restricted by CSI | Source restraints, constraints, internal frame and shell force/load accounting; reference version is older than ETABS 23, so corroborate the specific V23 assignment |
| G-M02 | Computers & Structures, Inc. | ETABS Frame End Length Offsets | ETABS help, version not specified in page | https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm | HTML | Automatic offsets, rigid zone factor and member force output stations |
| G-M03 | Computers & Structures, Inc. | Welcome to ETABS | ETABS 2016 edition | https://docs.csiamerica.com/manuals/etabs/Welcome%20to%20ETABS.pdf | Official public-readable PDF; redistribution restricted | ETABS object-to-analysis-element conversion and auto-mesh |
| G-M04 | OpenSees Project | eleLoad Command | Online current documentation, viewed 2026-11-12 | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/pattern/PlainPatternloadcommands/eleLoad.html | HTML | Beam uniform loads are local-axis reference loads; no blanket 3D Corotational support |
| G-M05 | OpenSees Project | Rigid Diaphragm | Online current docs, viewed 2026-11-12 | https://openseesdocumentation.readthedocs.io/en/latest/user/manual/model/mp_constraint/rigidDiaphragm.html | HTML | Rigid diaphragm in-plane X/Y/RZ for ndm=3 ndf=6; transformation and small-rotation assumption |
| G-M06 | OpenSeesPy / OpenSees Project | 2D Column Dynamic EQ Example | Online documentation, viewed 2026-11-12 | https://openseespydoc.readthedocs.io/en/latest/src/columneq.html | HTML | Static gravity LoadControl and loadConst(-time,0) prior to dynamic history |
| G-M07 | OpenSeesPy / OpenSees Project | reactions() and nodeReaction() | Online documentation, viewed 2026-11-12 | https://openseespydoc.readthedocs.io/en/latest/src/reactions.html and https://openseespydoc.readthedocs.io/en/latest/src/nodeReaction.html | HTML | Recompute/assemble reaction vector before reading nodal reactions |

**Technical review:** [2026-11-12 32/76/97 load-path evidence](../../REVIEW_MAIN/01_GRAVITY/20261112_GRAVITY_GUI_AND_LOAD_PATH_EVIDENCE_REVIEW.md). This review distinguishes external manual statements from project-specific data, model assumptions and numerical evidence.

**Copying policy:** keep copyrighted publisher PDFs at the official website, do not push external full texts to the publicly accessible repository. Reference URLs are not acceptance evidence; verify each claim against the original named section and current software version. No journal/citation count is invented.
