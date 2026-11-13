# Main launcher staged workflow regression

**Source:** tests/test_main_launcher_workflow_layout.py.

**Purpose:** Verify a navigation-only change retains the existing research launcher callbacks, source EDB selections, exact export controls, custom model tooling and main log.

**Inputs:** Source-only AST; no live ETABS, OpenSees, external access, data upload or Tk display.

**Checks:** Seven stage names, one typed global tool search, 41 original static tool registrations plus the four saved view callbacks, scrollbars and copy/jump controls, preserved ETABS import and rebuild commands.

**Run:** python -m unittest discover -s tests -p 'test_main_launcher_workflow_layout.py' -v.

**Limitations:** Static tests cannot demonstrate actual Tk geometry at Windows DPI or native solver correctness. GUI hand-testing and source model verification remain mandatory.
