"""Regression for Excel-native ETABS sheets with a false million-row used range.

No native ETABS, model modification or gravity solver involved.
"""
import unittest
from components.validation.etabs_assignment_gravity_audit import _rows


class FakeSheet:
    max_row=1_048_576
    def __init__(self,gapped=False):
        self.reset=False
        self.gapped=gapped
    def reset_dimensions(self):
        self.reset=True
    def iter_rows(self,*,min_row,max_row,values_only):
        assert min_row==1 and max_row<=100_000 and values_only
        yield ('Frame Assignments',None)
        yield ('UniqueName','Design Type')
        yield ('-', '-')
        yield ('1','BEAM')
        if self.gapped:yield (None,None)
        yield ('2','COLUMN')
        for _ in range(128):
            yield (None,None)
        # Must never visit a fabricated row > 1048576
        raise AssertionError('Blank tail should be ignored, not traversed')


class FakeWorkbook(dict):
    pass


class NativeWorkbookRangeTests(unittest.TestCase):
    def test_styled_excel_tail_does_not_overrun(self):
        sheet=FakeSheet()
        data=_rows(FakeWorkbook({'Frame Assigns - Summary':sheet}),'Frame Assigns - Summary')
        self.assertTrue(sheet.reset)
        self.assertEqual([r['UniqueName'] for r in data],['1','2'])
    def test_internal_gap_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'empty row'):
            _rows(FakeWorkbook({'Frame Assigns - Summary':FakeSheet(True)}),'Frame Assigns - Summary')


if __name__=='__main__':unittest.main()
