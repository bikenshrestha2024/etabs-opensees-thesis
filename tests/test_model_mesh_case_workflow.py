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

    def test_source_and_derived_config_have_separate_digest_evidence(self):
        original_sha={p:mesh.digest(self.root/p) for p in mesh.REQUIRED_SOURCE}
        optional_sha={"ETABS_Materials.csv":mesh.digest(self.root/"ETABS_Materials.csv")}
        path=mesh.stage_case(self.root,8)
        manifest=json.loads((path/"MESH_CASE_PROVENANCE.json").read_text())
        self.assertEqual(manifest["original_source_file_sha256"],
                         {**original_sha, **optional_sha})
        name=mesh.REQUIRED_SOURCE[3]
        self.assertEqual(manifest["original_source_file_sha256"][name],
                         mesh.digest(self.root/name))
        self.assertEqual(manifest["source_file_sha256"][name],
                         mesh.digest(path/name))
        self.assertNotEqual(manifest["source_file_sha256"][name],
                            manifest["original_source_file_sha256"][name])
        self.assertEqual(json.loads((self.root/name).read_text()),self.original)

    def test_symlinked_source_is_refused_before_run_creation(self):
        outside=self.root.parent/f"linked-source-{self.root.name}.json"
        outside.write_text('{"private":"do not copy"}')
        source=self.root/mesh.REQUIRED_SOURCE[0]
        source.unlink()
        try:
            source.symlink_to(outside)
        except (OSError,NotImplementedError):
            outside.unlink()
            self.skipTest("Host cannot create source symlinks")
        try:
            with self.assertRaisesRegex(ValueError,"linked mesh"):
                mesh.stage_case(self.root,4)
            self.assertFalse((self.root/"02_MODEL").exists())
            self.assertEqual(outside.read_text(),'{"private":"do not copy"}')
        finally:
            outside.unlink()

    def test_symlinked_output_parent_is_refused_and_external_target_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            external=Path(td)/"external"
            external.mkdir()
            alias=self.root/"02_MODEL"
            try:
                alias.symlink_to(external,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Host cannot create directory symlinks")
            with self.assertRaisesRegex(ValueError,"linked mesh"):
                mesh.stage_case(self.root,8)
            self.assertEqual(list(external.iterdir()),[])
            with self.assertRaisesRegex(ValueError,"linked mesh"):
                mesh.prepared_configs(self.root)
            self.assertEqual(list(external.iterdir()),[])

    def test_prepared_configs_preflight_rejects_linked_8_before_writing_4(self):
        with tempfile.TemporaryDirectory() as td:
            outside=Path(td)/"external.json"
            outside.write_text('{"private":true}')
            target=self.root/"02_MODEL"/"SLAB_LOAD_PATH"/"PREPARED_CONFIGS"
            target.mkdir(parents=True)
            try:
                (target/"Model_Config_MESH_08.json").symlink_to(outside)
            except (OSError,NotImplementedError):
                self.skipTest("Host cannot create file symlinks")
            with self.assertRaisesRegex(ValueError,"linked mesh"):
                mesh.prepared_configs(self.root)
            self.assertFalse((target/"Model_Config_MESH_04.json").exists())
            self.assertEqual(outside.read_text(),'{"private":true}')

    def test_reject_prepared_config_with_changed_source_settings(self):
        mesh.prepared_configs(self.root)
        root_config=self.root/mesh.REQUIRED_SOURCE[3]
        x=json.loads(root_config.read_text());x["gravity_factors"]["Live"]=1.0
        root_config.write_text(json.dumps(x))
        with self.assertRaisesRegex(ValueError,"stale"):
            mesh.stage_case(self.root,8)

    def test_source_assembly_refuses_fractional_and_boolean_mesh_resolution(self):
        from components.model.assembly import _mesh_areas
        source_nodes={1:[0.0,0.0,0.0]}
        for bad in (8.9,4.1,8.0,True,False,"8.0",None):
            with self.subTest(value=repr(bad)):
                with self.assertRaisesRegex(ValueError,"exact integer"):
                    _mesh_areas(source_nodes,[],{},{},floor_subdivisions=bad)
        for good in (2,4,8,16,"8"):
            with self.subTest(good=repr(good)):
                nodes,shells,objects=_mesh_areas(
                    source_nodes,[],{},{},floor_subdivisions=good)
                self.assertEqual(nodes,source_nodes)
                self.assertEqual(shells,[])
                self.assertEqual(objects,{})

    def test_mesh_diagnostic_zip_is_separate_and_hash_verified(self):
        import zipfile
        for n in (4,8,16):
            folder=mesh.case_base(self.root,n)
            run=folder/"RUNS"/"RUN_TEST"
            run.mkdir(parents=True)
            (run/"MESH_BUILD_STATUS.json").write_text(
                json.dumps({"status":"STAGED_NOT_ASSEMBLED"}))
            (folder/"EXCEL").mkdir()
            (folder/"EXCEL"/"sample.xlsx").write_bytes(b"synthetic-only")
            zip_path=mesh.package_mesh_case(self.root,n)
            self.assertEqual(zip_path.name,f"MESH_{n:02d}.zip")
            self.assertEqual(zip_path.parent.name,"UPLOAD_PACKAGES")
            with zipfile.ZipFile(zip_path) as z:
                self.assertIsNone(z.testzip())
                names=z.namelist()
                self.assertIn(f"MESH_{n:02d}/RUNS/RUN_TEST/MESH_BUILD_STATUS.json",names)
                self.assertIn(f"MESH_{n:02d}/EXCEL/sample.xlsx",names)
                manifest=json.loads(z.read(f"MESH_{n:02d}/ZIP_SHA256_MANIFEST.json"))
                self.assertEqual(manifest["mesh_subdivisions"],n)
                self.assertEqual(manifest["status"],
                                 "DIAGNOSTIC_PACKAGE_NOT_SOLVER_ACCEPTANCE")
                self.assertEqual(
                    manifest["files"]["RUNS/RUN_TEST/MESH_BUILD_STATUS.json"],
                    mesh.digest(run/"MESH_BUILD_STATUS.json"))
            self.assertTrue((folder/"EXCEL"/"sample.xlsx").is_file())

    def test_reject_missing_audit_and_invalid_mesh(self):
        with self.assertRaises(ValueError):
            mesh.case_base(self.root,2)
        (self.root/"OpenSees_Element_Connectivity.json").unlink()
        with self.assertRaises(FileNotFoundError):
            mesh.stage_case(self.root,4)

if __name__=="__main__":
    unittest.main()
