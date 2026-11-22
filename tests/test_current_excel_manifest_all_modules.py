"""Source manifest is authoritative for all current-stage NBC Excel inputs.

Synthetic workbooks, not native ETABS physical verification.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook
from components.inputs.project_workbooks import source_workbooks


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ManifestAuthoritativeTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        self.edb=self.root/"ULTIMATE LOAD - TEST.EDB"
        self.edb.write_bytes(b"source model A")
        self.legacy=self.root/"excel"/"source"
        self.legacy.mkdir(parents=True)
        self.calculator=self.legacy/"NBC105_2025_Seismic_Calculator_ETABS_Direct Interaction - Copy.xlsx"
        self.scaling=self.legacy/"ULTIMATE LOAD  - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS_NBC105_RS_Scaling.xlsx"
        for filename in (self.calculator,self.scaling):
            wb=Workbook()
            wb.active.title="NBC Calculator"
            ws=wb.create_sheet("SCALING SUMMARY")
            ws["A4"]="Source EDB"
            ws["B4"]=str(self.edb)
            ws["A14"]="X";ws["B14"]=2.073
            ws["A15"]="Y";ws["B15"]=2.203
            wb.save(filename)
        self.manifest=self.root/"01_ETABS_EXPORT"/"00_MANIFEST"/"PROJECT_SOURCES.private.json"
        self.manifest.parent.mkdir(parents=True)

    def _write(self,sources):
        data={"source_edb_sha256":_sha(self.edb),"sources":{
            role:{"path":str(file),"sha256":_sha(file)} for role,file in sources.items()}}
        self.manifest.write_text(json.dumps(data),encoding="utf-8")

    def _source(self):
        return patch("components.inputs.project_workbooks._source_edb_path",
                     return_value=str(self.edb))

    def test_new_manifest_without_nbc_roles_never_scans_old_excel(self):
        self._write({"etabs_full_table":self.scaling})
        with self._source():
            self.assertEqual(source_workbooks(self.root,self.root,"ULS"),[None,None])
            self.assertEqual(source_workbooks(self.root,self.root,"SLS"),[None,None])

    def test_only_registered_source_roles_are_selected(self):
        self._write({"nbc_calculator":self.calculator,
                     "nbc_scaling_uls":self.scaling})
        with self._source():
            self.assertEqual(source_workbooks(self.root,self.root,"ULS"),
                             [self.calculator,self.scaling])
            self.assertEqual(source_workbooks(self.root,self.root,"SLS"),
                             [self.calculator,None])

    def test_modified_registered_excel_fails_instead_of_using_other_copy(self):
        self._write({"nbc_calculator":self.calculator,
                     "nbc_scaling_uls":self.scaling})
        self.scaling.write_bytes(self.scaling.read_bytes()+b"unexpected update")
        with self._source(),self.assertRaisesRegex(ValueError,"changed"):
            source_workbooks(self.root,self.root,"ULS")

    def test_registered_scaling_foreign_edb_fails_closed(self):
        self._write({"nbc_scaling_uls":self.scaling})
        from openpyxl import load_workbook
        wb=load_workbook(self.scaling)
        wb["SCALING SUMMARY"]["B4"]=str(self.root/"alien.EDB")
        wb.save(self.scaling)
        self._write({"nbc_scaling_uls":self.scaling})
        with self._source(),self.assertRaisesRegex(ValueError,"not byte-identical"):
            source_workbooks(self.root,self.root,"ULS")


if __name__=="__main__":
    unittest.main()
