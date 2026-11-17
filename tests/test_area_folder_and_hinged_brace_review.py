"""Source-only regression for area output navigation and hinged brace evidence.

No ETABS or native OpenSees/FSAM solver is exercised. The brace checks
verify export report metadata contracts, not connection constitutive behavior.
"""
import ast
import json
from pathlib import Path
import tempfile
import unittest

from components.sections.area_elements import area_output_directory

ROOT=Path(__file__).resolve().parents[1]


class AreaOutputFolderTests(unittest.TestCase):
    def test_selected_existing_output_directory_opens_without_creating(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.assertEqual(area_output_directory(root),root)
            self.assertFalse((root/"02_MODEL").exists())
            expected=root/"02_MODEL"/"AREA_INTEGRATION"
            expected.mkdir(parents=True)
            self.assertEqual(area_output_directory(root),expected)
            self.assertEqual(area_output_directory(topology_json=root/"topology.json"),expected)
            generated=root/"custom"/"Reviewed_Area_Call.py"
            generated.parent.mkdir()
            generated.write_text("# source-only call\\n",encoding="utf-8")
            self.assertEqual(area_output_directory(root,generated_output=generated),
                             generated.parent)

    def test_missing_export_directory_is_not_created(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"nonexistent"
            with self.assertRaises(FileNotFoundError):
                area_output_directory(target)
            self.assertFalse(target.exists())

    def test_gui_button_bound_to_safe_folder_resolution(self):
        source=(ROOT/"components/sections/area_elements.py").read_text(encoding="utf-8")
        self.assertIn('text="Open output folder"',source)
        self.assertIn('command=open_output_folder',source)
        self.assertIn('selected=area_output_directory(',source)
        self.assertIn('os.startfile(str(selected))',source)


class BraceReviewContractTests(unittest.TestCase):
    def test_completed_elastic_export_reports_assigned_tags_and_separate_nonlinear_limit(self):
        from components.model.assembly import prepare_complete_export
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)
            runtime=folder/'runtime_source'
            runtime.mkdir()
            release=[[False,False,False,True,True,True],
                     [False,False,False,False,True,True],[0.]*6,[0.]*6,0]
            nodes={1:[0.,0.,0.],2:[3.,0.,3.],3:[1.5,0.,1.5],
                   4:[0.,0.,3.],5:[3.,3.,3.],6:[0.,3.,3.]}
            sources={
                'OpenSees_Element_Connectivity.json':dict(
                    node_map=[dict(etabs_point_name=str(n),opensees_node_tag=n,
                                   coordinates_m=xyz) for n,xyz in nodes.items()],
                    elements=[dict(etabs_object='1308',element_tag=25049,
                                   category='BRACE',dimension='line_2_node',node_tags=[1,2]),
                              dict(etabs_object='A',category='FLOOR',dimension='area_polygon',
                                   node_tags=[4,2,5,6])],
                    rigid_diaphragm_groups=[dict(storey_number=1,master_xyz=[3.,0.,3.],
                                                slave_node_tags=[2])]),
                'OpenSees_Section_Assignment_Audit.json':dict(
                    frame_assignments=[dict(etabs_object='1308',assigned_section='Synthetic steel',
                                            section_type='rectangle',width_m=.3,depth_m=.3,
                                            E_kN_m2=2e8,G_kN_m2=8e7,weight_per_volume=78.5)],
                    area_assignments=[dict(etabs_area_object='A',assigned_property='Synthetic slab',
                                           property_type='slab',material_name='Concrete',thickness_m=.15,
                                           material_values=dict(E=3e7,poisson_ratio=.2,weight_per_volume=25))],
                    frame_distributed_load_assignments=[]),
                'OpenSees_Load_Conversion_Audit.json':dict(
                    applied_area_loads=[],base_supports=dict(node_tags=[1]),
                    etabs_load_pattern_self_weight_multipliers=[dict(pattern='Self Weight',multiplier=1)]),
                'OpenSees_Source_Model_Metadata_V118.json':dict(
                    present_units=6,pattern_types={},frames={'1308':{'GetReleases':release}}),
            }
            for name,value in sources.items():
                (folder/name).write_text(json.dumps(value),encoding='utf-8')
            messages=[]
            manifest,report=prepare_complete_export(folder,runtime_dir=runtime,
                                                    progress=messages.append)
            self.assertEqual(report['assembly_errors'],[])
            self.assertTrue(manifest['elastic_assembled'])
            member=report['hinged_brace_release_review']['members'][0]
            self.assertEqual(member['solver_element_tags'],[100001,100002])
            self.assertEqual(member['etabs_GetReleases_raw'],release)
            self.assertEqual(member['elastic_status'],'ASSEMBLED_SOURCE_END_RELEASES')
            self.assertEqual(member['reviewed_nonlinear_status'],
                             'BLOCKED_UNVERIFIED_CONNECTION_AND_BRACE')
            self.assertFalse(report['nonlinear_ready'])
            warning=next(w for w in report['warnings'] if 'ETABS frame unique ID 1308' in w)
            self.assertIn('100001, 100002',warning)
            self.assertNotIn('pending assembly',warning)
            self.assertNotIn('remains gated',warning)
            self.assertTrue(any('Conforming ShellMITC4 mesh' in m for m in messages))
            self.assertTrue(any('Frame segment connectivity' in m for m in messages))
            self.assertTrue(any('runtime' in m.lower() for m in messages))

    def test_raw_releases_and_three_id_namespaces_in_assembly_report(self):
        path=ROOT/"components/model/assembly.py"
        source=path.read_text(encoding="utf-8")
        ast.parse(source,filename=str(path))
        for key in ("hinged_brace_release_review","etabs_GetReleases_raw",
                    "etabs_unique_frame_id","opensees_topology_preview_tag",
                    "solver_element_tags","reviewed_nonlinear_status",
                    "BLOCKED_UNVERIFIED_CONNECTION_AND_BRACE"):
            with self.subTest(key=key):
                self.assertIn(key,source)
        # The future solver tags are computed from the actual frame element
        # insertion sequence, not a topology preview or an ETABS frame ID.
        self.assertIn('100000+len(frame_elements)',source)
        self.assertIn('if e.get(\'hinged_brace\'): raise ValueError',source)


if __name__=="__main__":
    unittest.main()
