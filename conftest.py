"""Pytest configuration: optional platform dependencies become SKIPS, nothing else.

Headless Linux CI has no tkinter, plotly or ETABS COM bridge.  A test (or a test
module at import time) whose failure is exactly ``ModuleNotFoundError`` for one of
those named modules is reported as skipped.  Assertion failures and every other
exception, including ImportError/ModuleNotFoundError for any other module, still
fail.  Set ``THESIS_STRICT_OPTIONAL_IMPORTS=1`` (full Windows/Spyder environment)
to disable the conversion so a missing GUI/COM dependency fails loudly.
"""
import os

import pytest

OPTIONAL_MODULES = frozenset({
    "tkinter", "_tkinter",            # GUI
    "plotly",                          # interactive figures
    "comtypes", "win32com", "pythoncom", "pywintypes",  # ETABS COM (Windows)
})


def _strict():
    return os.environ.get("THESIS_STRICT_OPTIONAL_IMPORTS", "") not in ("", "0")


def _optional_name(exc):
    """Missing optional module name if exc is a ModuleNotFoundError for one, else None."""
    if not isinstance(exc, ModuleNotFoundError):
        return None
    root = (exc.name or "").split(".")[0]
    return root if root in OPTIONAL_MODULES else None


def _collect_message_name(message):
    # Collection reports keep only text: "ModuleNotFoundError: No module named 'tkinter'"
    prefix = "ModuleNotFoundError: No module named '"
    if not message.startswith(prefix) or not message.endswith("'"):
        return None
    root = message[len(prefix):-1].split(".")[0]
    return root if root in OPTIONAL_MODULES else None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    if _strict() or call.excinfo is None:
        return
    name = _optional_name(call.excinfo.value)
    if name is None:
        return
    rep = outcome.get_result()
    if rep.failed:
        rep.outcome = "skipped"
        rep.longrepr = (str(item.path), (item.reportinfo()[1] or 0) + 1,
                        f"Skipped: optional module '{name}' is not available")


@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    outcome = yield
    if _strict():
        return
    rep = outcome.get_result()
    if not rep.failed:
        return
    # A collection failure carries only text; the final "E   <Exception>: ..." line
    # is the raised (outermost) exception.
    lines = [ln for ln in str(rep.longrepr).splitlines() if ln.startswith("E  ")]
    name = _collect_message_name(lines[-1][1:].strip()) if lines else None
    if name is None:
        return
    rep.outcome = "skipped"
    rep.longrepr = (str(getattr(collector, "path", rep.nodeid)), 0,
                    f"Skipped: optional module '{name}' is not available")
