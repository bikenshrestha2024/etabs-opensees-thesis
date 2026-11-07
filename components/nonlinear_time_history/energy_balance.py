"""Relative-motion energy balance recorder for OpenSeesPy transient analysis.

[REF Uang & Bertero 1990, Earthquake Eng. Struct. Dyn. 19(1):77-90 (relative energy equation)]
[REF Christopoulos & Filiatrault 2006, Principles of Passive Supplemental Damping and Seismic Isolation, IUSS Press (energy formulation chapter)]
[REF Charney 2008, doi:10.1061/(ASCE)0733-9445(2008)134:4(581) (damping energy as a model check)]

Equation of relative motion under UniformExcitation (kN-m-s model), with the
gravity load P_g held constant after ``loadConst``:
    M u'' + C u' + R(u, u') = P_g - M iota a_g(t)
Integrating u'^T(.) dt from 0 to t gives
    E_K + E_D + E_S + E_V = E_I + W_G
E_I  relative input energy    = -integral(sum_i m_i u'_i a_g,i dt)
W_G  work of constant gravity = P_g . (u - u_0); P_g is recovered at start()
     from the assembled element resisting forces (static equilibrium), so
     P-Delta and axial-shortening work under gravity is balanced, not lost.
E_K  relative kinetic energy  = 1/2 sum_i m_i u'_i^2
E_D  Rayleigh damping energy  = integral(aM sum m u'^2 dt) + integral(f_bK . u' dt)
E_S  structural strain + hysteretic energy = sum_struct integral(F_e . du_e)
E_V  device energy (FVD, BRB, braces)       = sum_device integral(F_e . du_e)
Balance error = |E_I + W_G - (E_K+E_D+E_S+E_V)| / max(|E_I| history).

Element forces are ``ops.eleForce`` (static resisting force, global nodal
components); bK Rayleigh forces are ``ops.eleResponse(tag,'rayleighForces')``.
Integration is trapezoidal over each committed step, so the error contains the
integrator's O(dt^2) discretisation and Newmark (avg. accel.) is energy
conserving for the linear part. Recoverable strain energy is NOT separated from
dissipated hysteretic energy (requires unloading); E_S is their sum.

Units: energy in kN·m (= kJ). Outputs: CSV history and JSON summary.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

# [REF Uang & Bertero 1990] a closed balance within a few percent of the peak
# input energy is the conventional sanity check; 5% is a project default and
# must be stated in the thesis as an adopted tolerance, not a code limit.
DEFAULT_ENERGY_TOLERANCE = 0.05

COLUMNS = ('time_s', 'input_kJ', 'gravity_work_kJ', 'kinetic_kJ', 'rayleigh_kJ', 'strain_hysteretic_kJ',
           'device_kJ', 'sum_kJ', 'error_kJ', 'relative_error')


def _dot(a, b):
    return sum(float(x) * float(y) for x, y in zip(a, b))


class EnergyBalanceRecorder:
    """Accumulate the relative energy balance after each converged step.

    [REF Uang & Bertero 1990; Christopoulos & Filiatrault 2006]
    Inputs:
      ops                  OpenSeesPy module with a built, analysed domain.
      structural_tags      frame/core/slab element tags (E_S).
      device_tags          FVD/BRB/brace/link element tags (E_V).
      ground_accel         {dof(1-based): callable(t)->a_g in model units (m/s2)}.
      alpha_m, beta_k      Rayleigh coefficients in use (0 if none).
      rayleigh_tags        elements carrying bK (defaults to structural_tags).
    Call ``start(t0)`` once after gravity/loadConst and ``step(t)`` after
    each converged ``ops.analyze``.
    """

    def __init__(self, ops, *, structural_tags, device_tags=(), ground_accel,
                 alpha_m=0., beta_k=0., rayleigh_tags=None, mass_nodes=None):
        self.ops = ops
        self.structural = [int(t) for t in structural_tags]
        self.devices = [int(t) for t in device_tags]
        self.ground = {int(k): v for k, v in ground_accel.items()}
        self.alpha_m, self.beta_k = float(alpha_m), float(beta_k)
        self.rayleigh_tags = self.structural if rayleigh_tags is None else [int(t) for t in rayleigh_tags]
        nodes = ops.getNodeTags() if mass_nodes is None else mass_nodes
        self.mass = {}
        for n in nodes:
            ndf = len(ops.nodeDisp(n))
            m = [float(ops.nodeMass(n, d + 1)) for d in range(ndf)]
            if any(abs(x) > 0 for x in m):
                self.mass[int(n)] = m
        self._ele_nodes = {t: [int(n) for n in ops.eleNodes(t)]
                           for t in set(self.structural) | set(self.devices) | set(self.rayleigh_tags)}
        self.rows = []
        self.energy = dict(input=0., rayleigh=0., strain=0., device=0.)

    # -- state snapshots -------------------------------------------------
    def _ele_disp(self, tag):
        out = []
        for n in self._ele_nodes[tag]:
            out.extend(self.ops.nodeDisp(n))
        return out

    def _ele_vel(self, tag):
        out = []
        for n in self._ele_nodes[tag]:
            out.extend(self.ops.nodeVel(n))
        return out

    def _snapshot(self, t):
        ops = self.ops
        vel = {n: ops.nodeVel(n) for n in self.mass}
        # input power  -sum m v a_g ; mass-proportional damping power aM m v^2
        p_in = 0.
        p_am = 0.
        kin = 0.
        for n, m in self.mass.items():
            v = vel[n]
            for d, mi in enumerate(m):
                if mi == 0:
                    continue
                kin += .5 * mi * v[d] ** 2
                p_am += self.alpha_m * mi * v[d] ** 2
                ag = self.ground.get(d + 1)
                if ag is not None:
                    p_in -= mi * v[d] * float(ag(t))
        p_bk = 0.
        if self.beta_k:
            for tag in self.rayleigh_tags:
                f = ops.eleResponse(tag, 'rayleighForces')
                if f:
                    p_bk += _dot(f, self._ele_vel(tag))
        return dict(t=float(t), p_in=p_in, p_d=p_am + p_bk, kin=kin,
                    f={tag: list(ops.eleForce(tag)) for tag in self.structural + self.devices},
                    u={tag: self._ele_disp(tag) for tag in self.structural + self.devices})

    def start(self, t0=0.):
        """Record the reference state (energies zero at t0).

        Must be called on a converged static (gravity) state: the nodal sum of
        element resisting forces then equals the constant gravity load P_g.
        """
        self._prev = self._snapshot(t0)
        self._kin0 = self._prev['kin']
        load = {}
        for tag in self.structural + self.devices:
            f = self._prev['f'][tag]
            nodes = self._ele_nodes[tag]
            per = len(f) // len(nodes) if nodes else 0
            for k, n in enumerate(nodes):
                acc = load.setdefault(n, [0.] * per)
                for d in range(per):
                    acc[d] += f[k * per + d]
        self._gravity_load = load
        self._u0 = {n: list(self.ops.nodeDisp(n)) for n in load}
        self._append(t0)

    def _gravity_work(self):
        w = 0.
        for n, p in self._gravity_load.items():
            u = self.ops.nodeDisp(n)
            w += sum(pi * (ui - u0) for pi, ui, u0 in zip(p, u, self._u0[n]))
        return w

    def step(self, t):
        """Trapezoidal energy increments from the previous committed state."""
        cur = self._snapshot(t)
        prev = self._prev
        dt = cur['t'] - prev['t']
        self.energy['input'] += .5 * (prev['p_in'] + cur['p_in']) * dt
        self.energy['rayleigh'] += .5 * (prev['p_d'] + cur['p_d']) * dt
        for group, tags in (('strain', self.structural), ('device', self.devices)):
            inc = 0.
            for tag in tags:
                du = [b - a for a, b in zip(prev['u'][tag], cur['u'][tag])]
                inc += .5 * (_dot(prev['f'][tag], du) + _dot(cur['f'][tag], du))
            self.energy[group] += inc
        self._prev = cur
        self._append(t)

    def _append(self, t):
        e = self.energy
        kin = self._prev['kin'] - self._kin0
        wg = self._gravity_work()
        total = kin + e['rayleigh'] + e['strain'] + e['device']
        peak = max([abs(e['input'])] + [abs(r['input_kJ']) for r in self.rows]) or 0.
        err = e['input'] + wg - total
        self.rows.append(dict(time_s=float(t), input_kJ=e['input'], gravity_work_kJ=wg, kinetic_kJ=kin,
                              rayleigh_kJ=e['rayleigh'], strain_hysteretic_kJ=e['strain'],
                              device_kJ=e['device'], sum_kJ=total, error_kJ=err,
                              relative_error=(abs(err) / peak) if peak > 0 else 0.))

    # -- outputs ---------------------------------------------------------
    def summary(self, tolerance=DEFAULT_ENERGY_TOLERANCE):
        """Return the JSON-ready summary and PASS/FAIL against ``tolerance``.

        [REF Uang & Bertero 1990] error normalised by peak |E_I|.
        """
        return energy_balance_check(self.rows, tolerance)

    def write(self, folder, *, tolerance=DEFAULT_ENERGY_TOLERANCE, stem='Energy_Balance'):
        """Write ``<stem>.csv`` and ``<stem>.json`` into ``folder``; return summary."""
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / (stem + '.csv'), 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(self.rows)
        out = self.summary(tolerance)
        out.update(alphaM_per_s=self.alpha_m, betaKcomm_s=self.beta_k,
                   structural_element_count=len(self.structural),
                   device_element_count=len(self.devices),
                   mass_node_count=len(self.mass))
        (folder / (stem + '.json')).write_text(json.dumps(out, indent=2, allow_nan=False),
                                               encoding='utf-8')
        return out


def energy_balance_check(rows, tolerance=DEFAULT_ENERGY_TOLERANCE):
    """PASS when max |E_I - sum| / max |E_I| <= tolerance.

    [REF Uang & Bertero 1990] Input: rows with COLUMNS keys. Output: dict.
    A run with no input energy (zero excitation) is NOT_EVALUATED, not PASS.
    """
    tol = float(tolerance)
    if not math.isfinite(tol) or not 0 < tol < 1:
        raise ValueError('energy tolerance must be a fraction in (0, 1)')
    if not rows:
        return dict(status='NOT_EVALUATED_NO_STEPS', tolerance=tol)
    peak = max(abs(r['input_kJ']) for r in rows)
    if not all(math.isfinite(r[k]) for r in rows for k in COLUMNS):
        return dict(status='FAIL_NONFINITE', tolerance=tol)
    if peak <= 0:
        return dict(status='NOT_EVALUATED_NO_INPUT_ENERGY', tolerance=tol)
    worst = max(rows, key=lambda r: abs(r['error_kJ']))
    rel = abs(worst['error_kJ']) / peak
    last = rows[-1]
    return dict(
        status='PASS' if rel <= tol else 'FAIL',
        tolerance=tol, max_relative_error=rel, time_of_max_error_s=worst['time_s'],
        peak_input_kJ=peak,
        final=dict((k, last[k]) for k in COLUMNS),
        reference='[REF Uang & Bertero 1990; Christopoulos & Filiatrault 2006]',
        scope='Numerical energy-closure check; not a structural acceptance criterion',
    )
