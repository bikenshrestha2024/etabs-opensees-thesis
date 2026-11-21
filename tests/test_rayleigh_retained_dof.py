"""Native static regression for an SP on a retained diaphragm DOF."""
import pytest

from components.modal.rayleigh import _diaphragm_translation


def _solve(ops, steps, handler, restrained=True):
    ops.wipe()
    ops.model("basic", "-ndm", 3, "-ndf", 6)
    ops.node(1, 0, 0, 0)
    ops.node(2, 0, 0, 1)
    ops.node(3, 0, 1, 1)
    ops.fix(1, 1, 1, 1, 1, 1, 1)
    ops.fix(3, 0, 0, 1, 1, 1, int(restrained))
    ops.geomTransf("Linear", 1, 0, 1, 0)
    ops.element("elasticBeamColumn", 1, 1, 2, 1, 100, 50, 1, 1, 1, 1)
    ops.rigidDiaphragm(3, 3, 2)
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(3, 1, 0, 0, 0, 0, 0)
    ops.constraints(handler)
    ops.numberer("RCM")
    ops.system("UmfPack")
    ops.test("NormDispIncr", 1e-10, 10)
    ops.algorithm("Newton")
    ops.integrator("LoadControl", 1 / steps)
    ops.analysis("Static")
    assert ops.analyze(steps) == 0
    ops.reactions()
    physical, _ = _diaphragm_translation(ops, 3, [2], 1)
    return physical, ops.nodeDisp(3, 1), ops.nodeReaction(1, 1)


def test_rayleigh_translation_is_step_invariant():
    ops = pytest.importorskip("openseespy.opensees")
    try:
        single = _solve(ops, 1, "Transformation")
        multi = _solve(ops, 10, "Transformation")
        control = _solve(ops, 10, "Lagrange")
        assert single[0] == pytest.approx(1 / 300)
        assert multi[0] == pytest.approx(single[0])
        assert multi[0] == pytest.approx(control[0])
        assert multi[2] == pytest.approx(control[2])
        assert multi[2] == pytest.approx(-1)
        assert control[1] == pytest.approx(control[0])
        # OpenSees releases that fix the issue should also pass this check.
        ratio = multi[1] / multi[0]
        assert min(abs(ratio - 1), abs(ratio - 5.5)) < 1e-8
    finally:
        ops.wipe()


def test_rayleigh_rejects_inconsistent_or_rotating_floor():
    class Domain:
        def nodeDisp(self, node, dof):
            return {(2, 1): .02, (3, 1): .03, (2, 6): 0, (3, 6): .01}[node, dof]

    with pytest.raises(RuntimeError, match="rotation"):
        _diaphragm_translation(Domain(), 1, [2, 3], 1)
    domain = Domain()
    original = domain.nodeDisp
    domain.nodeDisp = lambda n, dof: 0. if dof == 6 else original(n, dof)
    with pytest.raises(RuntimeError, match="translations"):
        _diaphragm_translation(domain, 1, [2, 3], 1)


def test_empirical_rayleigh_rejects_inherited_full_gravity(tmp_path, monkeypatch):
    from components.modal.rayleigh import run

    monkeypatch.setenv("OPENSEES_GRAVITY_PROFILE", "GRAVITY_1.0D_1.0L")
    with pytest.raises(ValueError, match="assembled seismic preload"):
        run(tmp_path, 2.0, 2.0, empirical_settings={})
