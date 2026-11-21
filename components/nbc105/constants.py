"""Shared NBC 105:2025 constants. [REF NBC105-2025 notation list, printed p. 7]

GRAVITY_M_S2 is the single definition of g used by the Rayleigh period
(Eq. 5.1(1)), the weight-to-mass conversion in the model assembly and the
clause modules. USER_DECISION 2026-11-21 (recorded as USER_DECLARED, not
verified by the agent): use the higher-precision standard gravity 9.80665 m/s^2.
The NBC 105:2025 notation list (printed p. 7) says "g: acceleration due to
gravity, to be taken as 9.81 m/s^2"; the adopted value is smaller by
0.0341 % (1 - 9.80665/9.81), a documented deviation from the printed value.
"""
from __future__ import annotations

GRAVITY_M_S2: float = 9.80665
NBC_NOTATION_GRAVITY_M_S2: float = 9.81  # printed p. 7; reference only, not used in calculations
# PDF page = printed page + 21 up to printed p. 26; + 23 from printed p. 27 on
# (the Figure 4-3 page and a duplicate page numbered 26 shift it). Verify the
# foot number of every page read. The constant is the offset for p. <= 26 only.
PRINTED_PAGE_OFFSET: int = 21

__all__ = ["GRAVITY_M_S2", "NBC_NOTATION_GRAVITY_M_S2", "PRINTED_PAGE_OFFSET"]
