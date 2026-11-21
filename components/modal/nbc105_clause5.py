"""Backward-compatible shim: the clause 5 module moved to
``components/nbc105/clause_05_dynamic_characteristics.py``.

Every public name (functions and constants) is re-exported as the same object.
"""
from components.nbc105 import clause_05_dynamic_characteristics as _impl
from components.nbc105.clause_05_dynamic_characteristics import *  # noqa: F401,F403

__all__ = list(_impl.__all__)
