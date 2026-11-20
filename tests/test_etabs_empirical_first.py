import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "etabs_period_review"))
from reconcile import (
    empirical_reference, force_scale, matches_empirical_reference, rayleigh,
    reconcile, select_period, soil_c_modal_ch, soil_c_static_ch,
)

def test_rayleigh_uses_paired_signed_floors():
    result=rayleigh([{'story':'Story1','weight_kN':981.,'force_kN':10.,'displacement_m':.2,'rotation_rad':0.,'torsion_kNm':0.}])
    assert math.isclose(result['period_s'],2*math.pi*math.sqrt(981*.04/(9.80665*2.)))

def test_force_scale_is_floor_and_keeps_displacement_unscaled():
    assert force_scale(120,100)=={'force':1.0,'displacement':1.0}
    assert force_scale(80,100)=={'force':1.25,'displacement':1.0}

def test_noncentered_rows_fail():
    row={'story':'Story1','weight_kN':981.,'force_kN':10.,'displacement_m':.2,'rotation_rad':.001,'torsion_kNm':0.}
    with pytest.raises(ValueError, match="centered-case"):
        rayleigh([row])


def test_pending_axis_and_capped_manual_axis_are_independent():
    axes = reconcile(period_inputs={
        "X": {"automatic": None}, "Y": {"automatic": None, "manual_rayleigh": 2.5},
    })["directions"]
    assert axes["X"]["aw_m2"] == pytest.approx(2.073174515)
    assert axes["X"]["adopted_s"] is None
    assert axes["X"]["updated_esm_minimum_kN"] is None
    assert axes["Y"]["adopted_s"] == pytest.approx(1.921979777)


@pytest.mark.parametrize(("period", "shape"), [(0, 1), (0.1, 2.5), (1, 2.5), (4, 0.625), (6, 10 / 36)])
def test_modal_spectrum_corner_ordinates(period, shape):
    assert soil_c_modal_ch(period) == pytest.approx(shape)


def test_manual_and_automatic_period_selection():
    assert select_period(2, 1.8)["adopted_s"] == 1.8
    assert select_period(2, 1.8, manual_rayleigh=2.5)["adopted_s"] == 2
    assert select_period(2, 1.8, direct=2.5) == {
        "adopted_s": 2.5, "nbc_minimum_s": 1.8, "source": "DIRECT_OVERRIDE",
    }
    assert select_period(2, None, direct=0.5)["adopted_s"] == 0.5
    for invalid in (0, -1, float("nan")):
        with pytest.raises(ValueError, match="positive and finite"):
            select_period(2, 1.8, direct=invalid)
    with pytest.raises(ValueError, match="only one"):
        select_period(2, 1.8, manual_rayleigh=1, direct=1)
    with pytest.raises(ValueError, match="verified P-Delta"):
        select_period(2, None)


def test_static_spectrum_covers_manual_input_range():
    assert soil_c_static_ch(0.05) == 2.5
    assert soil_c_static_ch(2.5) == 1
    assert soil_c_static_ch(5) == 0.4
    with pytest.raises(ValueError, match="published Soil C"):
        soil_c_static_ch(6.1)


def test_empirical_first_gate_rejects_archived_exponent():
    for axis in "XY":
        ref = empirical_reference(axis)
        assert ref["k"] == pytest.approx(1 + (ref["period_s"] - 0.5) / 2)
        assert matches_empirical_reference(axis, round(ref["cd_uls"], 6), round(ref["k"], 6),
                                           round(ref["updated_esm_minimum_kN"], 4))
        assert not matches_empirical_reference(axis, ref["cd_uls"], ref["k"] + 0.01,
                                               ref["updated_esm_minimum_kN"])
    assert select_period(2, None, allow_pending=True)["adopted_s"] is None
