"""Evidence ZIP contract: local-only, immutable sources, fail-closed packages."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import unittest

from components.inputs.evidence_archive import publish_case_evidence_zip


class EvidenceZipTests(unittest.TestCase):
    def test_package_is_nonempty_and_checksums_match(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            one = root / 'result.json'; one.write_text('{"result":true}', encoding='utf-8')
            two = root / 'report.csv'; two.write_text('a,b\n1,2\n', encoding='utf-8')
            archive = publish_case_evidence_zip(
                root, filename='Modal_ULS_Evidence.zip',
                files=[('02_RESULTS/result.json',one),('03_EXCEL/report.csv',two)],
                status='COMPLETED_SOLVER_ONLY_NATIVE_EQUIVALENCE_NOT_VERIFIED')
            self.assertEqual(archive, root / '07_EXPORT_ZIP' / 'Modal_ULS_Evidence.zip')
            with ZipFile(archive) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(len(z.namelist()), 3)
                self.assertEqual(z.read('02_RESULTS/result.json'), one.read_bytes())
                manifest=json.loads(z.read('EVIDENCE_MANIFEST.json'))
                self.assertEqual(manifest['engineering_acceptance'],'NOT_VERIFIED')
                for e in manifest['files']:
                    self.assertEqual(hashlib.sha256(z.read(e['archive_path'])).hexdigest(),e['sha256'])
                    self.assertNotIn(str(root),json.dumps(e))

    def test_missing_input_does_not_publish_partial_archive(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaises(FileNotFoundError):
                publish_case_evidence_zip(root,filename='Modal.zip',files=[('lost.csv',root/'lost.csv')])
            self.assertFalse((root/'07_EXPORT_ZIP'/'Modal.zip').exists())

    def test_refuses_empty_archive_and_unsafe_paths(self):
        with TemporaryDirectory() as td:
            root=Path(td);source=root/'data.json';source.write_text('{}')
            with self.assertRaises(ValueError):
                publish_case_evidence_zip(root,filename='empty.zip',files=[])
            for arcname in ('../escape.json','/absolute.json','EVIDENCE_MANIFEST.json'):
                with self.subTest(arcname=arcname),self.assertRaises(ValueError):
                    publish_case_evidence_zip(root,filename='unsafe.zip',files=[(arcname,source)])
            with self.assertRaises(ValueError):
                publish_case_evidence_zip(root,filename='unsafe.zip',files=[('same',source),('same',source)])

    def test_dedicated_category_and_linked_source_are_not_accepted(self):
        with TemporaryDirectory() as td:
            root=Path(td);src=root/'data.json';src.write_text('{}')
            archive=publish_case_evidence_zip(root,filename='Area_Inventory.zip',category='AREA_INTEGRATION',files=[('inputs/topology.json',src)])
            self.assertEqual(archive.parent,root/'07_EXPORT_ZIP'/'AREA_INTEGRATION')
            link=root/'alias.json'
            try:link.symlink_to(src)
            except (OSError,NotImplementedError):return
            with self.assertRaises(ValueError):
                publish_case_evidence_zip(root,filename='unsafe.zip',files=[('inputs/link.json',link)])


    def test_existing_modal_run_is_packaged_without_solver(self):
        from components.modal.gui_and_reports import package_modal_evidence
        with TemporaryDirectory() as td:
            root=Path(td)
            for name in ('00_INPUT_SOURCE','01_LOGS','02_RESULTS','03_EXCEL','04_FIGURES','07_EXPORT_ZIP'):
                (root/name).mkdir()
            (root/'00_INPUT_SOURCE'/'CASE_MANIFEST.json').write_text('{"solver_status":"COMPLETED_SOLVER_ONLY"}')
            (root/'01_LOGS'/'NBC105_Modal_V111_run.log').write_text('EIGEN RETURN')
            (root/'02_RESULTS'/'NBC105_Modal_V111.json').write_text('{"limit_state":"ULS","returned_modes":40}')
            (root/'03_EXCEL'/'NBC105_Modal_V111.csv').write_text('mode,period\n1,2.4\n')
            zipped=package_modal_evidence(root,'ULS',canonical=True)
            self.assertEqual(zipped.parent,root/'07_EXPORT_ZIP')
            with ZipFile(zipped) as z:
                self.assertIn('02_RESULTS/NBC105_Modal_V111.json',z.namelist())
                self.assertIn('01_LOGS/NBC105_Modal_V111_run.log',z.namelist())
                self.assertIn('03_EXCEL/NBC105_Modal_V111.csv',z.namelist())
                self.assertIsNone(z.testzip())

    def test_modal_package_fails_without_result_json(self):
        from components.modal.gui_and_reports import package_modal_evidence
        with TemporaryDirectory() as td:
            root=Path(td)
            (root/'02_RESULTS').mkdir()
            with self.assertRaises(FileNotFoundError):
                package_modal_evidence(root,'ULS',canonical=True)

if __name__ == '__main__': unittest.main()
