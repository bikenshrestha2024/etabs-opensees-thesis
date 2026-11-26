"""Selectable storey seismic-weight allocation conventions for the §5.2 ledger.

Config key ``storey_mass_allocation_convention`` in ``OpenSees_Complete_Model_Config_V118.json``
(absent = default; the export is then byte-identical to the historical one):

``NBC_MID_HEIGHT_BASE_TO_FLOOR1`` (default, historical)
    NBC 105:2025 §5.2 mid-height rule between floors (``storey_index_for_elevation``);
    every node at or below floor 1, including free nodes at the base elevation, goes to floor 1.
``ETABS_BASE_ROW``
    As the default, but nodal weight at the base elevation (free z = base nodes) is
    excluded from every floor, like the ETABS ``Mass Summary by Story`` Base row, which is
    outside the diaphragm mass and outside W. In this building the only masses below the
    storey-1 mid-height sit at z = 0, so this equals a strict §5.2 reading in which the base
    (no lateral level) owns the lower half of storey 1.
``ETABS_BASE_ROW_LINEAR_SPLIT``
    Base row excluded as above, and every intermediate node is split linearly between the
    level below and the level above (share above = (z - z_below)/(z_above - z_below)); the
    level below storey 1 is the base (excluded). This reproduces the ETABS storey masses
    (Lump Mass = Yes) inferred from the ±215.463 kN roof/base fit in the 2026-11-21 run
    finding §7.2; it is an inferred ETABS convention, not the §5.2 mid-height rule.

Only the storey ledger (Wi used by Rayleigh, ESM and the mass audit) changes. Nodal masses
in the eigen problem stay at their own nodes for every convention.

[REF NBC105-2025 §5.2, printed p. 30] [REF docs/source/components/modal/storey_mass_convention.py.md]
"""
from __future__ import annotations

import math
from typing import Sequence

from components.nbc105.clause_05_dynamic_characteristics import storey_index_for_elevation

DEFAULT = "NBC_MID_HEIGHT_BASE_TO_FLOOR1"
ETABS_BASE_ROW = "ETABS_BASE_ROW"
ETABS_BASE_ROW_LINEAR_SPLIT = "ETABS_BASE_ROW_LINEAR_SPLIT"
CONVENTIONS = (DEFAULT, ETABS_BASE_ROW, ETABS_BASE_ROW_LINEAR_SPLIT)
BASE = -1
CONFIG_KEY = "storey_mass_allocation_convention"


def validate_convention(value):
    """Return the convention name; None (key absent) means the historical default.

    [REF docs/source/components/modal/storey_mass_convention.py.md]
    """
    if value is None:
        return DEFAULT
    if value not in CONVENTIONS:
        raise ValueError(f"Unknown {CONFIG_KEY} {value!r}; use one of " + ", ".join(CONVENTIONS))
    return value


def storey_shares(z_m: float, floor_elevations_m: Sequence[float], base_z_m: float,
                  convention: str = DEFAULT, *, tolerance_m: float = 1e-7):
    """Return [(floor_index, fraction), ...] for a node at ``z_m``; index ``BASE`` (-1) is excluded.

    [REF NBC105-2025 §5.2, printed p. 30] fractions sum to 1 and are all positive.
    """
    convention = validate_convention(convention)
    e = [float(v) for v in floor_elevations_m]
    z, base = float(z_m), float(base_z_m)
    if not (math.isfinite(z) and math.isfinite(base)):
        raise ValueError("Elevations must be finite")
    if not e or e[0] <= base:
        raise ValueError("Floor elevations must lie above the base")
    if convention == DEFAULT:
        return [(storey_index_for_elevation(z, e), 1.0)]
    if z <= base + tolerance_m:
        return [(BASE, 1.0)]
    if convention == ETABS_BASE_ROW:
        return [(storey_index_for_elevation(z, e), 1.0)]
    if z >= e[-1] - tolerance_m:
        return [(len(e) - 1, 1.0)]
    levels = [base] + e
    for j in range(1, len(levels)):
        if z <= levels[j] + tolerance_m:
            if z >= levels[j] - tolerance_m:
                return [(j - 1, 1.0)]
            upper = (z - levels[j - 1]) / (levels[j] - levels[j - 1])
            return [(j - 2, 1.0 - upper), (j - 1, upper)]
    return [(len(e) - 1, 1.0)]
