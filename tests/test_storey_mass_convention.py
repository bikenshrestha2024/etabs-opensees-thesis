"""Storey seismic-weight allocation conventions (default, ETABS base row, linear split)."""
import re
from pathlib import Path

import pytest

from components.modal.rayleigh_mass_audit import audit_rayleigh_mass_elevations
from components.modal.storey_mass_convention import (
    BASE, DEFAULT, ETABS_BASE_ROW, ETABS_BASE_ROW_LINEAR_SPLIT, storey_shares, validate_convention)
from components.nbc105.constants import GRAVITY_M_S2

FLOORS = [3.8, 7.6, 11.4]


def test_default_is_historical_mid_height_rule():
    assert validate_convention(None) == DEFAULT
    assert storey_shares(0.0, FLOORS, 0.0) == [(0, 1.0)]          # z = 0 goes to floor 1
    assert storey_shares(6.1, FLOORS, 0.0) == [(1, 1.0)]          # floor + 2.3 m goes up
    assert storey_shares(5.0, FLOORS, 0.0) == [(0, 1.0)]          # below mid-height goes down
    with pytest.raises(ValueError, match="Unknown"):
        validate_convention("UPWARD")


def test_etabs_base_row_excludes_only_base_elevation():
    assert storey_shares(0.0, FLOORS, 0.0, ETABS_BASE_ROW) == [(BASE, 1.0)]
    assert storey_shares(2.3, FLOORS, 0.0, ETABS_BASE_ROW) == [(0, 1.0)]
    assert storey_shares(6.1, FLOORS, 0.0, ETABS_BASE_ROW) == [(1, 1.0)]


def test_linear_split_matches_etabs_fit_and_conserves_weight():
    # floor + 2.3 m: 2.3/3.8 to the level above, 1.5/3.8 to the level below
    shares = storey_shares(6.1, FLOORS, 0.0, ETABS_BASE_ROW_LINEAR_SPLIT)
    assert [i for i, _ in shares] == [0, 1]
    assert shares[0][1] == pytest.approx(1.5 / 3.8) and shares[1][1] == pytest.approx(2.3 / 3.8)
    low = storey_shares(2.3, FLOORS, 0.0, ETABS_BASE_ROW_LINEAR_SPLIT)
    assert low[0][0] == BASE and low[0][1] == pytest.approx(1.5 / 3.8)
    assert storey_shares(7.6, FLOORS, 0.0, ETABS_BASE_ROW_LINEAR_SPLIT) == [(1, 1.0)]
    assert storey_shares(11.4, FLOORS, 0.0, ETABS_BASE_ROW_LINEAR_SPLIT) == [(2, 1.0)]
    # 545.839 kN per storey at floor + 2.3 m moves 545.839 x 1.5/3.8 = 215.463 kN down (§7.2)
    assert 545.839 * shares[0][1] == pytest.approx(215.463, abs=1e-3)


def _model():
    g = GRAVITY_M_S2
    return {"base_z_m": 0.0,
            "diaphragms": [{"master_tag": 101, "master_xyz": [0, 0, 3.8]},
                           {"master_tag": 102, "master_xyz": [0, 0, 7.6]}],
            "nodes": {"1": [0, 0, 0], "2": [0, 0, 0], "3": [0, 0, 3.8], "4": [0, 0, 6.1],
                      "5": [0, 0, 7.6]},
            "supports": {"1": [1, 1, 1, 1, 1, 1]},
            "nodal_mass": {"1": 50 / g, "2": 10 / g, "3": 100 / g, "4": 38 / g, "5": 80 / g}}


def _rows(w1, w2):
    return [{"master_node_tag": 101, "dead_load_kN": w1, "storage_live_load_kN": 0.,
             "other_live_load_kN": 0.},
            {"master_node_tag": 102, "dead_load_kN": w2, "storage_live_load_kN": 0.,
             "other_live_load_kN": 0.}]


def test_audit_follows_model_convention_and_reports_base_row():
    model = _model()
    default = audit_rayleigh_mass_elevations(model, _rows(110., 118.))
    assert default["base_row_excluded_weight_kN"] == 0.0
    assert default["storey_mass_allocation_convention"] == DEFAULT
    model["storey_mass_allocation_convention"] = ETABS_BASE_ROW
    base = audit_rayleigh_mass_elevations(model, _rows(100., 118.))
    assert base["base_row_excluded_weight_kN"] == pytest.approx(10.)
    split = audit_rayleigh_mass_elevations(model, _rows(115., 103.),
                                           convention=ETABS_BASE_ROW_LINEAR_SPLIT)
    assert split["floor_weights_from_nodal_mass_kN"] == pytest.approx([115., 103.])
    assert split["base_row_excluded_weight_kN"] + sum(split["floor_weights_from_nodal_mass_kN"]) \
        == pytest.approx(228.)
    with pytest.raises(ValueError, match="floor weights"):
        audit_rayleigh_mass_elevations(model, _rows(110., 118.))  # ETABS_BASE_ROW model, default rows


def test_no_superseded_gravity_literal_in_root_production_modules():
    root = Path(__file__).resolve().parents[1]
    offenders = [p.name for p in root.glob("*.py")
                 if re.search(r"9\.80665|9806\.65", p.read_text(encoding="utf-8", errors="ignore"))]
    assert offenders == []
