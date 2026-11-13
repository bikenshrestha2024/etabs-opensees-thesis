"""No native solver needed: isolated 02 Model 4/8/16 mesh stage evidence."""
import importlib.util
from pathlib import Path
import tempfile
import json
import unittest

SOURCE=Path(__file__).resolve().parents[1]/"components/gravity/mesh_cases.py"
SPEC=importlib.util.spec_from_file_location("mesh_cases_tested",SOURCE)
mesh=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mesh)


class MeshCasesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.original={
            "gravity_factors":{"Self Weight":1.0,"Live":0.3},
            "mass_factors":{"Self Weight":1.0,"Live":0.3},
            "floor_subdivisions":4,
            "slab_bending_factor":0.25,
        }
        for filename in mesh.REQUIRED_SOURCE:
            contents=self.original if filename.endswith("Config_V118.json") else {"source":filename}
            (self.root/filename).write_text(json.dumps(contents),encoding="utf-8")
        (self.root/"ETABS_Materials.csv").write_text("name,isotropic,weight_mass\n",encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_three_configurations_are_not_assembled_models(self):
        files=mesh.prepared_configs(self.root)
        self.assertEqual([p.name for p in files],
                         ["Model_Config_MESH_04.json","Model_Config_MESH_08.json","Model_Config_MESH_16.json"])
        self.assertEqual([json.loads(p.read_text())["floor_subdivisions"] for p in files],[4,8,16])
        self.assertFalse((self.root/"OpenSees_Complete_Model_Data_V118.json").exists())

    def test_stage_uses_three_distinct_runs_without_changing_root(self):
        before={p:mesh.digest(self.root/p) for p in mesh.REQUIRED_SOURCE}
        mesh.prepared_configs(self.root)
        dirs=[mesh.stage_case(self.root,n) for n in (4,8,16)]
        self.assertEqual(len(set(dirs)),3)
        for n,path in zip((4,8,16),dirs):
            self.assertEqual(n,json.loads((path/mesh.REQUIRED_SOURCE[3]).read_text())["floor_subdivisions"])
            self.assertEqual(json.loads((path/"MESH_CASE_PROVENANCE.json").read_text())["status"],"STAGED_NOT_ASSEMBLED")
            self.assertEqual(mesh.digest(self.root/"ETABS_Materials.csv"),mesh.digest(path/"ETABS_Materials.csv"))
        self.assertEqual(before,{p:mesh.digest(self.root/p) for p in mesh.REQUIRED_SOURCE})
        self.assertEqual(json.loads((self.root/mesh.REQUIRED_SOURCE[3]).read_text()),self.original)

    def test_reject_prepared_config_with_changed_source_settings(self):
        mesh.prepared_configs(self.root)
        root_config=self.root/mesh.REQUIRED_SOURCE[3]
        x=json.loads(root_config.read_text());x["gravity_factors"]["Live"]=1.0
        root_config.write_text(json.dumps(x))
        with self.assertRaisesRegex(ValueError,"stale"):
            mesh.stage_case(self.root,8)

    def test_reject_missing_audit_and_invalid_mesh(self):
        with self.assertRaises(ValueError):
            mesh.case_base(self.root,2)
        (self.root/"OpenSees_Element_Connectivity.json").unlink()
        with self.assertRaises(FileNotFoundError):
            mesh.stage_case(self.root,4)

if __name__=="__main__":
    unittest.main()
