"""Pure fake-CSI tests for native quantity table extraction and fail closed."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from components.validation.etabs_native_quantity_tables import (
    export_native_quantity_tables, extract_analytical_mesh, compare_analytical_mesh)


class FakeDatabase:
    def GetAvailableTables(self):
        return (2, ["Material List by Object Type", "Unrelated"],
                ["Material List by Object Type", "Other"], [0, 0], 0)

    def GetTableForDisplayArray(self, key, field_keys, group, version,
                                fields, count, data):
        if key != "Material List by Object Type":
            raise RuntimeError("Unexpected table requested")
        # Exact six-element OUT tuple captured from user's ETABS v23 OAPI:
        # FieldKeyList, TableVersion, FieldsKeysIncluded,
        # NumberRecords, TableData, retcode.
        return ((), 1, ("Object", "Weight"), 2,
                ("B1", "50.0", "S1", "30.0"), 0)


class FakeSap:
    DatabaseTables=FakeDatabase()


class EtabsNativeQuantityTests(unittest.TestCase):
    def test_native_analytical_points_elements_and_named_constraints(self):
        class Points:
            def GetNameList(self):return (4,["p1","p2","p3","p4"],0)
            def GetCoordCartesian(self,n):
                return (*{"p1":(0,0,0),"p2":(2,0,0),"p3":(2,0,3),"p4":(0,0,3)}[n],0)
            def GetRestraint(self,n):return ([n in ("p1","p2")]*6,0)
            def GetConstraint(self,n):
                return (1,[n],["edge1"],0) if n in ("p1","p2") else (0,[],[],0)
            def GetObj(self,n):return (n,1,0)
            def GetTransformationMatrix(self,n):return ([1,0,0,0,1,0,0,0,1],0)
        class Areas:
            def GetNameList(self):return (1,["a1"],0)
            def GetPoints(self,n):return (4,["p1","p2","p3","p4"],0)
            def GetObj(self,n):return ("Wall-A",0)
        class Lines:
            def GetNameList(self):return (1,["l1"],0)
            def GetPoints(self,n):return ("p1","p4",0)
            def GetObj(self,n):return ("Column-A",2,0.,1.,0)
        sap=FakeSap()
        sap.GetPresentUnits=lambda:6
        sap.PointElm=Points();sap.AreaElm=Areas();sap.LineElm=Lines()
        report=extract_analytical_mesh(sap)
        self.assertEqual(report["point_count"],4)
        self.assertEqual(report["base_analytical_point_ids"],["p1","p2"])
        self.assertEqual(report["named_constraint_membership"],{"edge1":["p1","p2"]})
        self.assertEqual(report["elements"][0]["source_object"]["name"],"Wall-A")
        self.assertEqual(report["engineering_acceptance"],"NOT_VERIFIED")
        self.assertEqual(report["internal_mpc_coefficients"],"NOT_RECOVERED_BY_NAMED_CONSTRAINT_QUERY")
        self.assertFalse(report["errors"])
        sap.LineElm.GetPoints=lambda n:("p1","absent",0)
        sap.PointElm.GetConstraint=lambda n:(1,[],[],0)
        report=extract_analytical_mesh(sap)
        self.assertEqual(report["status"],"PARTIAL_NATIVE_API_EVIDENCE")
        self.assertEqual(len(report["errors"]),5)
        self.assertIsNone(report["elements"][1]["points"])
        sap.GetPresentUnits=lambda:5
        with self.assertRaisesRegex(ValueError,"kN-m-C"):
            extract_analytical_mesh(sap)

    def test_mesh_comparison_connectivity_and_ambiguity(self):
        coords=[(0,0,0),(2,0,0),(2,0,3),(0,0,3)]
        native=dict(schema="etabs-analytical-mesh-native-v1",units="kN,m,C",
            points=[dict(id=str(i),xyz_m=p) for i,p in enumerate(coords,1)],
            elements=[dict(kind="AREA_ELM",id="a",points=["3","4","1","2"],
                           source_object=dict(name="W"))])
        solved=dict(ok=True,nodes=[dict(tag=i,x_m=p[0],y_m=p[1],z_m=p[2])
                                  for i,p in enumerate(coords,1)],
                    elements=[dict(tag=100001,nodes=[1,2,3,4])])
        domain=dict(frames=[],shells=[dict(object="W",nodes=[1,2,3,4])])
        report=compare_analytical_mesh(native,solved,domain)
        self.assertEqual(report["status"],"CONNECTIVITY_MATCHED_DIAGNOSTIC")
        self.assertEqual(report["matched_points"],4)
        self.assertEqual(report["engineering_acceptance"],"NOT_VERIFIED")
        native["elements"][0]["points"]=["4","3","2","1"]
        self.assertEqual(len(compare_analytical_mesh(native,solved,domain)["reversed_area_cycles"]),1)
        native["elements"][0]["points"]=["1","3","2","4"]
        self.assertEqual(compare_analytical_mesh(native,solved,domain)["matched_elements"],0)
        native["elements"][0]["points"]=["1","2","3","4"]
        solved["nodes"][1].update(x_m=0.)
        report=compare_analytical_mesh(native,solved,domain)
        self.assertEqual(report["matched_elements"],0)
        self.assertEqual(len(report["ambiguous_native_points"]),1)
        domain["shells"][0]["nodes"]=[1,3,2,4]
        with self.assertRaisesRegex(ValueError,"crosswalk"):
            compare_analytical_mesh(native,solved,domain)

    def test_capture_actual_fields_and_data(self):
        with tempfile.TemporaryDirectory() as root:
            result=export_native_quantity_tables(FakeSap(),root)
            self.assertEqual(result["available_table_count"],2)
            self.assertEqual(result["selected_table_count"],1)
            row=result["table_exports"][0]
            self.assertEqual(row["status"],"EXPORTED_RAW_NOT_NORMALIZED")
            path=Path(root)/row["file"]
            with path.open(encoding="utf-8-sig",newline="") as stream:
                records=list(csv.reader(stream))
            self.assertEqual(records,
                             [["Object","Weight"],["B1","50.0"],["S1","30.0"]])
            self.assertTrue((Path(root)/"ETABS_NATIVE_QUANTITY_MANIFEST.json").is_file())

    def test_gravity_selection_and_all_evidence_families(self):
        class Native(FakeDatabase):
            cases=["EQX"]
            combos=["Old"]
            def GetLoadCasesSelectedForDisplay(self):
                return (len(self.cases),self.cases,0)
            def GetLoadCombinationsSelectedForDisplay(self):
                return (len(self.combos),self.combos,0)
            def SetLoadCasesSelectedForDisplay(self,values):
                self.cases=list(values);return 0
            def SetLoadCombinationsSelectedForDisplay(self,values):
                self.combos=list(values);return 0
            def GetAvailableTables(self):
                names=["Element Connectivity - Shells","Joint Assignments - Constraints",
                       "Section Cut Forces","Element Joint Forces - Frames",
                       "Joint Reactions","Other"]
                return (len(names),names,names,[0]*len(names),0)
            def GetTableForDisplayArray(self,key,*args):
                if self.cases or self.combos!=["1. DL + LL"]:
                    raise AssertionError("wrong display selection")
                if key=="Section Cut Forces":
                    return ((),1,("OutputCase",),0,(),0)
                return ((),1,("OutputCase",),1,("1. DL + LL",),0)
        sap=FakeSap();sap.DatabaseTables=Native()
        with tempfile.TemporaryDirectory() as root:
            result=export_native_quantity_tables(sap,root,gravity_combo="1. DL + LL")
            self.assertEqual(result["selected_table_count"],5)
            self.assertEqual(result["analytical_mesh_api"]["status"],"NATIVE_ANALYTICAL_MESH_UNAVAILABLE")
            self.assertTrue((Path(root)/"ETABS_NATIVE_ANALYTICAL_MESH.json").is_file())
            self.assertEqual(result["display_selection_status"],"GRAVITY_COMBO_READBACK_VERIFIED")
            self.assertEqual(result["engineering_evidence_coverage"]["analytical_mesh"]["status"],
                             "RAW_NONEMPTY_CANDIDATES_REQUIRE_REVIEW")
            self.assertEqual(result["engineering_evidence_coverage"]["beam_end_offsets"]["status"],
                             "NO_CATALOG_CANDIDATES")
            cut=next(row for row in result["table_exports"] if row["table_key"]=="Section Cut Forces")
            self.assertEqual(cut["records"],0)
            self.assertNotIn("Section Cut Forces",result["engineering_evidence_coverage"]["foundation_section_cuts"]["nonempty_tables"])
            self.assertEqual(sap.DatabaseTables.cases,["EQX"])
            self.assertEqual(sap.DatabaseTables.combos,["Old"])

    def test_gravity_selection_unavailable_does_not_claim_scope(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(AttributeError):
                export_native_quantity_tables(FakeSap(),root,gravity_combo="1. DL + LL")
            self.assertFalse((Path(root)/"ETABS_NATIVE_QUANTITY_MANIFEST.json").exists())

    def test_rejects_nonzero_native_return(self):
        class Failed(FakeDatabase):
            def GetTableForDisplayArray(self,*args):
                return ((),1,("Object","Weight"),1,("B1","50"),1)
        sap=FakeSap();sap.DatabaseTables=Failed()
        with tempfile.TemporaryDirectory() as root:
            result=export_native_quantity_tables(sap,root)
            self.assertEqual(result["table_exports"][0]["status"],
                             "UNAVAILABLE_OR_API_ERROR")
            self.assertIn("retcode=1",result["table_exports"][0]["error"])

    def test_malformed_native_data_is_reported_not_fabricated(self):
        class Broken(FakeDatabase):
            def GetTableForDisplayArray(self,*args):
                return ((),1,("Object","Weight"),2,("B1","50"),0)
        instance=FakeSap()
        instance.DatabaseTables=Broken()
        with tempfile.TemporaryDirectory() as root:
            result=export_native_quantity_tables(instance,root)
            self.assertEqual(result["table_exports"][0]["status"],
                             "UNAVAILABLE_OR_API_ERROR")
            self.assertEqual(result["table_exports"][0].get("records"),None)


if __name__=="__main__":
    unittest.main()
