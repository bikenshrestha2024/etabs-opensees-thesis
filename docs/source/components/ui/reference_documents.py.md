# `components/ui/reference_documents.py` — NBC 105 citation reference viewer

**Purpose:** Open the repository-maintained `docs/02_MODEL_NBC_REFERENCE_AND_VALIDATION.md` inside the Tkinter app when the user chooses **Open full formula/citation document**. The former code used `os.startfile(Path(__file__).with_name("NBC105_FORMULA_REFERENCE_V116.md"))`, but that file did not exist beside the UI module.

**Input:** Trusted relative document path beneath the active code repository. The source reference and validation document distinguishes NBC 105:2025, supplemental IS 16700:2023, ETABS, OpenSees, engineering examples and unresolved model evidence.

**Implementation:** Resolve from `components/ui/reference_documents.py` two parent levels upward. Reject escaping paths, missing files and files larger than 2 MB. Read UTF-8-SIG text, and show it in a Tk Text widget with both scrollbars; allow copying and saving a separate local copy. On missing/inaccessible content show a descriptive error rather than unhandled `os.startfile` failure. The function does not modify the original source documentation or run ETABS/OpenSees.

**Why the size guard?** Long-running numerical solves and enormous output logs should never be loaded in a GUI text widget. This viewer is for a bounded reference chapter, not analysis history or a PDF viewer.

**Verification:** `tests/test_model_citation_viewer.py` tests current doc resolution, bound, missing file, path traversal, and launcher wiring without creating a GUI display. GUI interactive verification on Windows remains recommended.

**Limits:** A code source, clause, or published reference is not proof that the selected ETABS model uses that parameter. Official standards should be checked against the actual published edition and project design basis. See the numbered `REVIEW_MAIN/00_MODEL` review and `LITERATURE` source register.
