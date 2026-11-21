"""Opt-in wall mesh refinement (``wall_max_cell_size_m``) and shell mesh audit.

[REF docs/source/components/model/shell_mesh_quality.py.md]
Synthetic panels only; the production ``_mesh_areas`` and
``prepare_complete_export`` paths are called. No ETABS, no OpenSees solve and
no user evidence files are needed. Passing tests show mesh geometry and load
bookkeeping only, not ETABS equivalence or engineering acceptance.
"""
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

from components.model.assembly import _mesh_areas, prepare_complete_export
from components.model.shell_mesh_quality import (
    audit_shell_mesh_quality, validate_wall_max_cell_size)

ROOT = Path(__file__).resolve().parents[1]
SLAB = dict(assigned_property='Slab150', property_type='slab', material_name='M45',
            thickness_m=.15, material_values=dict(E=3.354102e7, poisson_ratio=.2,
                                                  weight_per_volume=24.9926))
WALL = dict(assigned_property='Wall600', property_type='wall', material_name='M45',
            thickness_m=.6, material_values=dict(E=3.354102e7, poisson_ratio=.2,
                                                 weight_per_volume=24.9926))
# Corner (x=6) wall B1 has a 2.3 m level from its neighbour B2/B3; wall A2
# (plane y=0) does not, so the historical mesh has one T-junction node.
NODES = {1: [0., 0., 0.], 2: [3., 0., 0.], 3: [6., 0., 0.], 4: [0., 0., 3.8],
         5: [3., 0., 3.8], 6: [6., 0., 3.8], 7: [6., 2., 0.], 8: [6., 4., 0.],
         9: [6., 2., 3.8], 10: [6., 4., 3.8], 11: [6., 2., 2.3], 12: [6., 4., 2.3],
         13: [0., 4., 3.8]}
PANELS = (('A1', 'SHEAR WALL', [1, 2, 5, 4]), ('A2', 'SHEAR WALL', [2, 3, 6, 5]),
          ('B1', 'SHEAR WALL', [3, 7, 9, 6]), ('B2', 'SHEAR WALL', [7, 8, 12, 11]),
          ('B3', 'SHEAR WALL', [11, 12, 10, 9]), ('F', 'FLOOR', [4, 6, 10, 13]))
# sha256 of the default mesh (nodes + shells) produced by the code BEFORE the
# option existed (commit 1d76ce0); the historical mesh must stay identical.
GOLDEN_DEFAULT_SHA256 = 'e9a6506b91dcf75cdc455475131022f0e12669dbe9af902c3ad6980c289d9123'


def _records():
    return [dict(dimension='area_polygon', category=c, etabs_object=o, node_tags=n)
            for o, c, n in PANELS]


def _rows():
    return {o: dict(SLAB if c == 'FLOOR' else WALL) for o, c, _ in PANELS}


def _mesh(**kw):
    return _mesh_areas(dict(NODES), _records(), _rows(), {}, 4, **kw)


def _digest(nodes, shells):
    body = json.dumps(dict(nodes={str(k): v for k, v in sorted(nodes.items())},
                           shells=[dict(object=s['object'], nodes=s['nodes'],
                                        area=round(s['area'], 12)) for s in shells]),
                      sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()


def _by_cat(shells, cat):
    return [s for s in shells if s['category'] == cat]


class ValidationTests(unittest.TestCase):
    def test_accepts_positive_numbers_and_none(self):
        self.assertIsNone(validate_wall_max_cell_size(None))
        self.assertEqual(validate_wall_max_cell_size(1), 1.0)
        self.assertEqual(validate_wall_max_cell_size(0.75), 0.75)

    def test_rejects_bad_values(self):
        for bad in (0, -1., float('nan'), float('inf'), True, False, '1.0', [1.]):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'wall_max_cell_size_m'):
                validate_wall_max_cell_size(bad)
            with self.subTest(mesher=bad), self.assertRaisesRegex(ValueError, 'wall_max_cell_size_m'):
                _mesh(wall_max_cell_size_m=bad)


class DefaultMeshTests(unittest.TestCase):
    def test_default_matches_pre_option_golden(self):
        nodes, shells, _ = _mesh()
        self.assertEqual(len(shells), 28)
        self.assertEqual(len(_by_cat(shells, 'SHEAR WALL')), 12)
        self.assertEqual(len(nodes), 39)
        self.assertEqual(_digest(nodes, shells), GOLDEN_DEFAULT_SHA256)
        explicit = _mesh(wall_max_cell_size_m=None)
        self.assertEqual(_digest(explicit[0], explicit[1]), GOLDEN_DEFAULT_SHA256)

    def test_limit_larger_than_every_cell_is_a_no_op(self):
        nodes, shells, _ = _mesh(wall_max_cell_size_m=100.)
        self.assertEqual(_digest(nodes, shells), GOLDEN_DEFAULT_SHA256)

    def test_default_audit_reports_historical_wall_cells(self):
        nodes, shells, _ = _mesh()
        audit = audit_shell_mesh_quality(nodes, shells, floor_subdivisions=4)
        wall = audit['categories']['SHEAR WALL']
        self.assertEqual(audit['status'], 'DIAGNOSTIC_MESH_GEOMETRY_ONLY_NOT_ACCEPTANCE')
        self.assertNotIn('ACCEPT', audit['status'].replace('NOT_ACCEPTANCE', ''))
        self.assertAlmostEqual(wall['max_edge_m'], 3.8)
        self.assertEqual(wall['wall_vertical_extent_distinct_m'], [1.5, 2.3, 3.8])
        self.assertAlmostEqual(wall['max_aspect_ratio'], 3.8/1.5)
        self.assertEqual(audit['hanging_node_count'], 1)  # (6, 0, 2.3) on wall A2
        self.assertIsNone(audit['wall_max_cell_size_satisfied'])


class RefinedMeshTests(unittest.TestCase):
    def test_isolated_6m_by_3p8m_wall_grid(self):
        nodes = {1: [0., 0., 0.], 2: [6., 0., 0.], 3: [6., 0., 3.8], 4: [0., 0., 3.8]}
        records = [dict(dimension='area_polygon', category='SHEAR WALL',
                        etabs_object='W', node_tags=[1, 2, 3, 4])]
        base = _mesh_areas(nodes, records, {'W': dict(WALL)}, {}, 4)[1]
        self.assertEqual(len(base), 1)  # historical: one 6 x 3.8 m cell
        out, shells, _ = _mesh_areas(nodes, records, {'W': dict(WALL)}, {}, 4,
                                     wall_max_cell_size_m=1.0)
        self.assertEqual(len(shells), 6*4)
        audit = audit_shell_mesh_quality(out, shells, wall_max_cell_size_m=1.0)
        wall = audit['categories']['SHEAR WALL']
        self.assertAlmostEqual(wall['wall_width_max_m'], 1.0)
        self.assertAlmostEqual(wall['wall_vertical_extent_max_m'], .95)
        self.assertLessEqual(wall['max_aspect_ratio'], 4.)
        self.assertAlmostEqual(wall['max_aspect_ratio'], 1/.95)
        self.assertTrue(audit['wall_max_cell_size_satisfied'])
        self.assertAlmostEqual(sum(s['area'] for s in shells), 6*3.8, places=12)

    def test_refined_grid_counts_and_conformity(self):
        nodes, shells, by_obj = _mesh(wall_max_cell_size_m=1.0)
        counts = {o: len(c) for o, c in by_obj.items()}
        self.assertEqual(counts, dict(A1=20, A2=20, B1=10, B2=6, B3=4, F=32))
        audit = audit_shell_mesh_quality(nodes, shells, wall_max_cell_size_m=1.0)
        self.assertEqual(audit['hanging_node_count'], 0)
        self.assertTrue(audit['wall_max_cell_size_satisfied'])
        wall = audit['categories']['SHEAR WALL']
        self.assertLessEqual(wall['max_edge_m'], 1.0+1e-12)
        self.assertLessEqual(wall['max_aspect_ratio'], 4.)
        self.assertEqual(wall['cells_aspect_gt_4'], 0)

    def test_new_nodes_shared_by_adjacent_walls_and_floor(self):
        nodes, shells, by_obj = _mesh(wall_max_cell_size_m=1.0)
        tags = {o: {n for c in cells for n in c['nodes']} for o, cells in by_obj.items()}
        def at(pred):
            return {n for n, p in nodes.items() if pred(p)}
        # Coplanar A1/A2 share the whole x = 3 line, including new heights.
        x3 = at(lambda p: abs(p[0]-3) < 1e-9 and abs(p[1]) < 1e-9)
        self.assertEqual(len(x3), 6)
        self.assertTrue(x3 <= tags['A1'] and x3 <= tags['A2'])
        # Perpendicular A2/B1 share the corner line (6, 0, z) at every level.
        corner = at(lambda p: abs(p[0]-6) < 1e-9 and abs(p[1]) < 1e-9)
        self.assertEqual(len(corner), 6)
        self.assertTrue(corner <= tags['A2'] and corner <= tags['B1'])
        # Every wall top-edge node at z = 3.8 is a floor node, and vice versa.
        top_wall = {n for o in ('A1', 'A2', 'B1', 'B3') for n in tags[o]
                    if abs(nodes[n][2]-3.8) < 1e-9}
        edge_floor = {n for n in tags['F'] if abs(nodes[n][1]) < 1e-9
                      or abs(nodes[n][0]-6) < 1e-9}
        self.assertEqual(top_wall, edge_floor)
        self.assertIn(next(iter(at(lambda p: abs(p[0]-.75) < 1e-9 and abs(p[1]) < 1e-9
                                   and abs(p[2]-3.8) < 1e-9))), tags['F'])

    def test_area_and_self_weight_totals_preserved(self):
        _, base, base_obj = _mesh()
        _, refined, refined_obj = _mesh(wall_max_cell_size_m=1.0)
        def weight(cells):
            return sum(c['area']*c['properties']['thickness']*c['properties']['weight']
                       for c in cells)
        for obj in base_obj:
            self.assertAlmostEqual(sum(c['area'] for c in refined_obj[obj]),
                                   sum(c['area'] for c in base_obj[obj]), places=12)
        self.assertLess(abs(weight(refined)/weight(base)-1.), 1e-12)

    def test_node_tags_do_not_collide_with_source_tags(self):
        nodes, shells, _ = _mesh(wall_max_cell_size_m=1.0)
        for tag, xyz in NODES.items():
            self.assertEqual(nodes[tag], xyz)
        coordinates = [tuple(round(x, 8) for x in p) for p in nodes.values()]
        self.assertEqual(len(coordinates), len(set(coordinates)))
        self.assertTrue(all(len(set(c['nodes'])) == 4 for c in shells))


class AuditHandExampleTests(unittest.TestCase):
    def test_hand_built_cells(self):
        nodes = {1: [0, 0, 0], 2: [1, 0, 0], 3: [1, 1, 0], 4: [0, 1, 0],
                 5: [1, 0, 0], 6: [5, 0, 0], 7: [5, .5, 0], 8: [1, .5, 0],
                 9: [0, 0, 0], 10: [.1, 0, 0], 11: [.1, 0, 3.8], 12: [0, 0, 3.8]}
        shells = [dict(category='FLOOR', nodes=[1, 2, 3, 4], area=1.),
                  dict(category='FLOOR', nodes=[5, 6, 7, 8], area=2.),
                  dict(category='SHEAR WALL', nodes=[9, 10, 11, 12], area=.38)]
        audit = audit_shell_mesh_quality(nodes, shells)
        floor, wall = audit['categories']['FLOOR'], audit['categories']['SHEAR WALL']
        self.assertEqual(floor['cell_count'], 2)
        self.assertAlmostEqual(floor['min_edge_m'], .5)
        self.assertAlmostEqual(floor['max_edge_m'], 4.)
        self.assertAlmostEqual(floor['max_aspect_ratio'], 8.)
        self.assertEqual((floor['cells_aspect_gt_4'], floor['cells_aspect_gt_10']), (1, 0))
        self.assertAlmostEqual(floor['total_area_m2'], 3.)
        self.assertAlmostEqual(wall['max_aspect_ratio'], 38.)
        self.assertEqual((wall['cells_aspect_gt_4'], wall['cells_aspect_gt_10'],
                          wall['cells_aspect_gt_50']), (1, 1, 0))
        self.assertAlmostEqual(wall['wall_width_min_m'], .1)
        self.assertAlmostEqual(wall['wall_vertical_extent_max_m'], 3.8)
        # Node 10 (0.1,0,0) lies inside edge 1-2 and node 8 (1,0.5,0) inside
        # edge 2-3: two T-junctions. Coincident tags 2/5 are edge ends only.
        self.assertEqual(audit['hanging_node_count'], 2)
        self.assertEqual(audit['hanging_node_sample'], [8, 10])


def _write_export(folder, cfg_extra=None):
    """Synthetic evidence-free export: the walls/floor above, one column, supports."""
    xyz = dict(NODES)
    frames = [dict(etabs_object='C1', dimension='line_2_node', category='COLUMN', node_tags=[1, 4])]
    areas = [dict(etabs_object=o, dimension='area_polygon', category=c, node_tags=n)
             for o, c, n in PANELS]
    topology = dict(
        node_map=[dict(etabs_point_name=str(n), opensees_node_tag=n, coordinates_m=q)
                  for n, q in xyz.items()],
        elements=frames+areas,
        rigid_diaphragm_groups=[dict(storey_number=1, diaphragm_name='D1', master_xyz=[3, 2, 3.8],
                                     slave_node_tags=[4, 5, 6, 9, 10, 13])])
    section = dict(
        frame_assignments=[dict(etabs_object='C1', assigned_section='Col', section_type='rectangle',
                                width_m=.6, depth_m=.6, E_kN_m2=3.354102e7, G_kN_m2=1.3975e7,
                                weight_per_volume=24.9926)],
        area_assignments=[dict(etabs_area_object=o, **(SLAB if c == 'FLOOR' else WALL))
                          for o, c, _ in PANELS],
        frame_distributed_load_assignments=[])
    loads = dict(direct_uniform_loads_status='READ', uniform_load_sets_status='READ',
                 applied_area_loads=[dict(object='F', pattern='Live', direction_code=6,
                                          coordinate_system='Global', value=-4.)],
                 etabs_load_pattern_self_weight_multipliers=[dict(pattern='Self Weight', multiplier=1)],
                 base_supports=dict(node_tags=[1, 2, 3, 7, 8]))
    for name, data in (('OpenSees_Element_Connectivity.json', topology),
                       ('OpenSees_Section_Assignment_Audit.json', section),
                       ('OpenSees_Load_Conversion_Audit.json', loads),
                       ('OpenSees_Source_Model_Metadata_V118.json',
                        {'pattern_types': {}, 'scope': 'synthetic test fixture',
                         'supports': {str(n): [1]*6 for n in (1, 2, 3, 7, 8)}})):
        (folder/name).write_text(json.dumps(data), encoding='utf-8')
    if cfg_extra is not None:
        factors = {'Self Weight': 1., 'Live': .3}
        cfg = dict(gravity_factors=factors, mass_factors=factors, frame_section_mapping={},
                   nonlinear_parameters_reviewed=False, nonlinear_materials_file='',
                   nonlinear_wall_fsam_tags={}, section_overrides={}, area_property_overrides={})
        cfg.update(cfg_extra)
        (folder/'OpenSees_Complete_Model_Config_V118.json').write_text(json.dumps(cfg), encoding='utf-8')


class SyntheticExportTests(unittest.TestCase):
    def _run(self, cfg_extra):
        tmp = tempfile.TemporaryDirectory(dir=ROOT/'tests', prefix='wall_mesh_fixture_')
        self.addCleanup(tmp.cleanup)
        folder = Path(tmp.name)
        _write_export(folder, cfg_extra)
        _manifest, report = prepare_complete_export(folder, runtime_dir=ROOT)
        self.assertEqual(report['assembly_errors'], [], report.get('assembly_traceback'))
        data = json.loads((folder/'OpenSees_Complete_Model_Data_V118.json').read_text(encoding='utf-8-sig'))
        cfg = json.loads((folder/'OpenSees_Complete_Model_Config_V118.json').read_text(encoding='utf-8-sig'))
        return report, data, cfg

    def test_default_export_records_audit_and_keeps_config_key_absent(self):
        report, data, cfg = self._run({})
        self.assertNotIn('wall_max_cell_size_m', cfg)
        self.assertIsNone(report['wall_max_cell_size_m'])
        audit = report['shell_mesh_quality_audit']
        self.assertEqual(audit['status'], 'DIAGNOSTIC_MESH_GEOMETRY_ONLY_NOT_ACCEPTANCE')
        self.assertEqual(audit['categories']['SHEAR WALL']['cell_count'], 12)
        self.assertEqual(audit['categories']['FLOOR']['cell_count'], 16)
        self.assertEqual(audit['hanging_node_count'], 1)
        self.assertNotIn('shell_mesh_quality_audit', data)

    def test_refined_export_preserves_totals_cuts_column_and_records_setting(self):
        base, base_data, _ = self._run({})
        report, data, cfg = self._run({'wall_max_cell_size_m': 1.0})
        self.assertEqual(cfg['wall_max_cell_size_m'], 1.0)
        self.assertEqual(report['wall_max_cell_size_m'], 1.0)
        self.assertTrue(report['shell_mesh_quality_audit']['wall_max_cell_size_satisfied'])
        self.assertEqual(report['shell_mesh_quality_audit']['hanging_node_count'], 0)
        # Active horizontal weight excludes fixed-base node mass, so it moves
        # when base cells get smaller; the totals must not move.
        for key in ('total_downward_load_kN', 'total_seismic_weight_including_fixed_nodes_kN'):
            self.assertLess(abs(report[key]/base[key]-1.), 1e-9, key)
        for pattern, value in base['gravity_by_pattern_kN'].items():
            self.assertLess(abs(report['gravity_by_pattern_kN'][pattern]/value-1.), 1e-9)
        self.assertLess(report['story_ledger_mass_error_percent'], 1e-7)
        self.assertLess(abs(report['story_ledger_active_weight_kN']
                            -report['active_horizontal_seismic_weight_kN']), 1e-6)
        for audit, key in (('slab_weight_audit', 'equivalent_nodal_slab_self_weight_kN'),
                           ('slab_weight_audit', 'total_source_floor_area_m2'),
                           ('joint_volume_weight_audit', 'gross_RCC_weight_kN'),
                           ('storey_gravity', 'assembled_total_kN')):
            self.assertLess(abs(report[audit][key]/base[audit][key]-1.), 1e-9, key)
        # Column C1 on the wall edge x=0, y=0 is cut at every refined wall node.
        col = [f for f in data['frames'] if f['object'] == 'C1']
        base_col = [f for f in base_data['frames'] if f['object'] == 'C1']
        self.assertEqual(len(base_col), 1)
        self.assertEqual(len(col), 5)
        self.assertAlmostEqual(sum(f['length'] for f in col), 3.8)
        self.assertLess(abs(sum(data['nodal_mass'].values())/sum(base_data['nodal_mass'].values())-1.), 1e-9)

    def test_edge_propagated_base_supports_cover_new_base_nodes(self):
        policy = {'wall_base_restraint_policy': 'EDGE_PROPAGATE_CONFIRMED',
                  'etabs_wall_auto_mesh_restraints_confirmed': True}
        base, base_data, _ = self._run(dict(policy))
        report, data, _ = self._run(dict(policy, wall_max_cell_size_m=1.0))
        base_nodes = {n for n, p in data['nodes'].items() if abs(p[2]) < 1e-9}
        on_wall_base = {n for n in base_nodes
                        if abs(data['nodes'][n][1]) < 1e-9 or abs(data['nodes'][n][0]-6) < 1e-9}
        self.assertEqual(on_wall_base, set(data['supports']))
        self.assertGreater(len(report['added_wall_mesh_support_tags']),
                           len(base['added_wall_mesh_support_tags']))

    def test_source_only_policy_adds_no_new_base_supports(self):
        report, data, _ = self._run({'wall_max_cell_size_m': 1.0})
        self.assertEqual(report['added_wall_mesh_support_tags'], [])
        self.assertEqual(set(data['supports']), {'1', '2', '3', '7', '8'})

    def test_invalid_config_value_blocks_assembly(self):
        tmp = tempfile.TemporaryDirectory(dir=ROOT/'tests', prefix='wall_mesh_fixture_')
        self.addCleanup(tmp.cleanup)
        folder = Path(tmp.name)
        _write_export(folder, {'wall_max_cell_size_m': 'one'})
        _manifest, report = prepare_complete_export(folder, runtime_dir=ROOT)
        self.assertTrue(any('wall_max_cell_size_m' in e for e in report['assembly_errors']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
