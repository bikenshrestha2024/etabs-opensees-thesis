"""Native OpenSeesPy checks for region-based Rayleigh damping and energy balance.

[REF Charney 2008, doi:10.1061/(ASCE)0733-9445(2008)134:4(581)]
[REF Uang & Bertero 1990, Earthquake Eng. Struct. Dyn. 19(1):77-90]

These use a SMALL 3D test model (fibre column, elastic beams, ShellMITC4
slab, rigid diaphragm, Steel01 corotTruss brace, Maxwell FVD twoNodeLink).
They verify OpenSees behaviour that the building runner relies on; they do
NOT verify the thesis building. Skipped (not passed) when OpenSeesPy is absent.
"""
import math
import unittest

try:
    import openseespy.opensees as ops
except Exception:  # pragma: no cover - environment dependent
    ops = None

from components.nonlinear_time_history.damping_regions import (
    apply_structural_rayleigh, classify_elements, resolve_inherent_damping_ratio,
    DEFAULT_INHERENT_DAMPING_RATIO, NBC105_FIVE_PERCENT)
from components.nonlinear_time_history.energy_balance import (
    EnergyBalanceRecorder, energy_balance_check)

DT = 0.005
STEPS = 600
FVD_TAG, BRACE_TAG = 50, 40


def ag(t):
    """Two-frequency synthetic ground acceleration, m/s2 (test input only)."""
    return 3.0 * math.sin(2 * math.pi * 1.2 * t) * min(1., t / .5) + 1.0 * math.sin(2 * math.pi * 4. * t)


def ag_strong(t):
    """Single-frequency stronger input for the P-Delta gravity-work test."""
    return 4.0 * math.sin(2 * math.pi * 1.2 * t) * min(1., t / .5)


def build(*, brace_do_rayleigh=False, gravity=False, column_half=.2, gravity_kN=-400., motion=None):
    motion = motion or ag
    ops.wipe(); ops.model('basic', '-ndm', 3, '-ndf', 6)
    h, b = 3.5, 6.0
    base = {1: (0, 0), 2: (b, 0), 3: (b, b), 4: (0, b)}
    for n, (x, y) in base.items():
        ops.node(n, x, y, 0.); ops.fix(n, 1, 1, 1, 1, 1, 1)
        ops.node(n + 10, x, y, h)
    ops.node(100, b / 2, b / 2, h); ops.fix(100, 0, 0, 1, 1, 1, 0)
    ops.rigidDiaphragm(3, 100, 11, 12, 13, 14)
    # Nonlinear fibre column section (Steel01 fibres, test values only).
    ops.uniaxialMaterial('Steel01', 1, 3.45e5, 2.0e8, .02)
    ops.section('Fiber', 1, '-GJ', 1e5)
    ops.patch('rect', 1, 6, 6, -column_half, -column_half, column_half, column_half)
    ops.geomTransf('PDelta', 1, 1, 0, 0)
    ops.geomTransf('Linear', 2, 0, 0, 1)
    ops.beamIntegration('Lobatto', 1, 1, 4)
    for i, n in enumerate(base, 1):
        ops.element('forceBeamColumn', i, n, n + 10, 1, 1)
    ops.element('elasticBeamColumn', 21, 11, 12, .2, 3e7, 1.2e7, 1e-3, 2e-3, 2e-3, 2)
    ops.element('elasticBeamColumn', 22, 14, 13, .2, 3e7, 1.2e7, 1e-3, 2e-3, 2e-3, 2)
    ops.section('ElasticMembranePlateSection', 2, 3e7, .2, .2, 0.)
    ops.element('ShellMITC4', 30, 11, 12, 13, 14, 2)
    ops.uniaxialMaterial('Steel01', 3, 3.45e5, 2.0e8, .01)
    ops.element('corotTruss', BRACE_TAG, 1, 13, .002, 3,
                *(('-doRayleigh', 1) if brace_do_rayleigh else ()))
    ops.uniaxialMaterial('ViscousDamper', 4, 5e4, 800., .4)
    ops.element('twoNodeLink', FVD_TAG, 2, 14, '-mat', 4, '-dir', 1,
                '-orient', -b, b, h, 0, 0, 1)
    for n in (11, 12, 13, 14):
        ops.mass(n, 20., 20., 20., 0., 0., 0.)
    ops.mass(100, 0., 0., 0., 0., 0., 50.)   # diaphragm-only rotational mass
    if gravity:
        # Static gravity, then loadConst: tests the constant-load work term.
        ops.timeSeries('Linear', 8); ops.pattern('Plain', 8, 8)
        for n in (11, 12, 13, 14):
            ops.load(n, 0., 0., gravity_kN, 0., 0., 0.)
        ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('UmfPack')
        ops.test('NormDispIncr', 1e-10, 50); ops.algorithm('Newton')
        ops.integrator('LoadControl', .1); ops.analysis('Static')
        assert ops.analyze(10) == 0
        ops.loadConst('-time', 0.); ops.wipeAnalysis()
    ops.timeSeries('Path', 7, '-time', *[i * DT for i in range(STEPS + 2)],
                   '-values', *[motion(i * DT) for i in range(STEPS + 2)])
    ops.pattern('UniformExcitation', 7, 1, '-accel', 7)
    ops.constraints('Transformation'); ops.numberer('RCM'); ops.system('UmfPack')
    ops.test('NormDispIncr', 1e-10, 50); ops.algorithm('Newton')
    ops.integrator('Newmark', .5, .25); ops.analysis('Transient')


def run(damping, *, recorder=False, brace_do_rayleigh=False, gravity=False, motion=None, **model):
    motion = motion or ag
    build(brace_do_rayleigh=brace_do_rayleigh, gravity=gravity, motion=motion, **model)
    am, bk = 0.4, 0.002
    audit = None
    if damping == 'global':
        ops.rayleigh(am, 0., 0., bk)
    elif damping == 'region':
        audit = apply_structural_rayleigh(ops, am, bk)
    rec = None
    if recorder:
        groups = classify_elements(ops)
        rec = EnergyBalanceRecorder(ops, structural_tags=groups['structural'],
                                    device_tags=groups['excluded'], ground_accel={1: motion},
                                    alpha_m=am if damping != 'none' else 0.,
                                    beta_k=bk if damping != 'none' else 0.)
        rec.start(0.)
    hist = []
    for i in range(STEPS):
        if ops.analyze(1, DT) != 0:
            raise RuntimeError('test model failed to converge')
        hist.append(ops.nodeDisp(100, 1))
        if rec:
            rec.step(ops.getTime())
    return hist, audit, rec


@unittest.skipIf(ops is None, 'OpenSeesPy not installed: native checks NOT run')
class RegionRayleigh(unittest.TestCase):
    def test_region_equals_global_for_current_element_families(self):
        g, _, _ = run('global')
        r, audit, _ = run('region')
        self.assertEqual(sorted(audit['excluded_element_tags']), [BRACE_TAG, FVD_TAG])
        self.assertLess(max(abs(a - b) for a, b in zip(g, r)), 1e-9 * max(map(abs, g)) + 1e-12)

    def test_region_removes_stiffness_damping_from_opted_in_device(self):
        # A brace/BRB truss created with '-doRayleigh 1' DOES take bK under the
        # global command; the region form must remove it (Charney 2008).
        g, _, _ = run('global', brace_do_rayleigh=True)
        r, _, _ = run('region', brace_do_rayleigh=True)
        self.assertGreater(max(abs(a - b) for a, b in zip(g, r)), 1e-6 * max(map(abs, g)))

    def test_region_equals_global_with_mass_on_diaphragm_master_only(self):
        def master_mass(kind):
            build()
            for n in (11, 12, 13, 14):
                ops.mass(n, 0., 0., 0., 0., 0., 0.)
            ops.mass(100, 80., 80., 0., 0., 0., 300.)
            audit = ops.rayleigh(.4, 0., 0., .002) if kind == 'global' else apply_structural_rayleigh(ops, .4, .002)
            out = []
            for _ in range(STEPS):
                self.assertEqual(ops.analyze(1, DT), 0)
                out.append(ops.nodeDisp(100, 1))
            return out, audit
        g, _ = master_mass('global')
        r, audit = master_mass('region')
        self.assertEqual(audit['orphan_mass_node_tags'], [100])
        self.assertLess(max(abs(a - b) for a, b in zip(g, r)), 1e-9 * max(map(abs, g)) + 1e-12)

    def test_energy_balance_closes(self):
        _, _, rec = run('region', recorder=True)
        summary = energy_balance_check(rec.rows, tolerance=.02)
        self.assertEqual(summary['status'], 'PASS', summary)
        final = summary['final']
        self.assertGreater(final['device_kJ'], 0.)
        self.assertGreater(final['rayleigh_kJ'], 0.)
        self.assertGreater(final['input_kJ'], 0.)

    def test_energy_balance_closes_with_constant_gravity_and_p_delta(self):
        # Slender, heavily loaded columns: constant-gravity work is material.
        _, _, rec = run('region', recorder=True, gravity=True, motion=ag_strong,
                        column_half=.06, gravity_kN=-2500.)
        summary = energy_balance_check(rec.rows, tolerance=.002)
        self.assertEqual(summary['status'], 'PASS', summary)
        without_gravity_work = max(abs(r['error_kJ'] - r['gravity_work_kJ'])
                                   for r in rec.rows) / summary['peak_input_kJ']
        # Dropping W_G must worsen closure by a clear margin (measured ~13x).
        self.assertGreater(without_gravity_work, 5 * summary['max_relative_error'])


class Configuration(unittest.TestCase):
    def test_default_and_explicit_five_percent(self):
        self.assertEqual(resolve_inherent_damping_ratio({}), DEFAULT_INHERENT_DAMPING_RATIO)
        self.assertEqual(resolve_inherent_damping_ratio({'inherent_damping_five_percent': True}),
                         NBC105_FIVE_PERCENT)
        with self.assertRaises(ValueError):
            resolve_inherent_damping_ratio({'inherent_damping_ratio': .05})
        with self.assertRaises(ValueError):
            resolve_inherent_damping_ratio({'inherent_damping_ratio': 5.0,
                                            'inherent_damping_five_percent': True})
        self.assertEqual(resolve_inherent_damping_ratio({'inherent_damping_ratio': .02}), .02)

    def test_energy_check_rejects_zero_input(self):
        rows = [dict(time_s=0., input_kJ=0., gravity_work_kJ=0., kinetic_kJ=0., rayleigh_kJ=0.,
                     strain_hysteretic_kJ=0., device_kJ=0., sum_kJ=0., error_kJ=0.,
                     relative_error=0.)]
        self.assertEqual(energy_balance_check(rows)['status'], 'NOT_EVALUATED_NO_INPUT_ENERGY')


if __name__ == '__main__':
    unittest.main()
