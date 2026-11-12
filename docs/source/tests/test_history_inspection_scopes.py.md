# Test guide: test_history_inspection_scopes.py

**What:** pure unit tests ensuring the saved-history viewer opens a study-scoped list rather than silently mixing LTH and 0.1-s exploratory NL reports.  
**When:** changed `history_inspection.py` grouping or browsing functionality.  
**Why:** mixing different model/record/assumption scopes would make otherwise correctly recorded numerical results misleading.  
**How:** temporary directory path tests and scope-choice tests; five deterministic assertions; never invokes native OpenSees or opens Tk widgets.  
**Where:** `tests/test_history_inspection_scopes.py`, source `components/ui/history_inspection.py`.  
**Which:** relative folder names, no real user paths; baseline ZIPs remain read-only and private.  
**Who:** Python UI maintainer evaluates passed tests and native GUI; structural reviewer checks engineering compatibility when comparing scopes.  
**Command:** `python -m unittest discover -s tests -p 'test_history_inspection_scopes.py' -v`.

**Limitations:** correct path grouping is not numerical convergence, physical source equivalence or code compliance. Real Windows Tk speed and picker behavior are still pending native inspection.

## 2026-11-12 refreshed control behavior

Additional test confirms the explicit `All analyses (mixed)` selection persists after the browser refreshes; initial default selection remains the linear study when available. This is a UI/metadata test, not a native response test.
