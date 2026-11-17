# workbook_publishing.py — atomic XLSX evidence publisher

**Canonical source:** [components/gravity/workbook_publishing.py](../../../../components/gravity/workbook_publishing.py)

**Purpose:** One shared XLSX publishing boundary used by the on-demand gravity workbook and mesh-specific Slab_Load_Path_MESH_04/08/16 workbook workflows. Formula and FEM calculations stay in their original modules. This helper handles only serialized artifact integrity.

**Public API:** publish_workbook(workbook, destination, temp_prefix=".gravity_") -> str returns the SHA256 of final workbook bytes. Target must be an XLSX under a non-symlinked path. An exclusive temporary XLSX in the target directory is saved first. Validate ZIP central directory and workbook parts ([Content_Types].xml and xl/workbook.xml); compute SHA256 via streamed 1 MiB reads (never load entire workbook into RAM); finally replace the destination atomically with os.replace. Temporary files are deleted on all failures.

**Failure behavior:** Interrupted XLSX serialization, corrupt ZIP or locked destination leaves any prior destination intact. Storey-gravity caller records FORMULA_WORKBOOK_EXPORT_FAILED. Mesh-specific caller does not publish a success manifest on failure. ZIP and checksum checks do NOT evaluate formulas, prove source-model equivalence, verify support reactions, or certify convergence.

**Security:** Refuse symbolic-link destination and ancestors before preparing output and again before committing. OS-level TOCTOU concurrency cannot be fully eliminated without fd-relative APIs. No ETABS, OpenSees or source-model modification.

**Regression:** tests/test_deferred_storey_workbook.py, tests/test_mesh_workbook_publication.py. Native follow-up: Windows Excel-open file locks, source-matched EDB/config output, full-gravity vs preload source factors, and separate beam/wall/support reactions.
