"""Direct, read-only export of the selected model's OpenSees material library.

Run from any working directory:
  python 08_EXPORT_MATERIAL_SECTION_LIBRARY.py "D:/Thesis Opensees/ETABS .../1"
This exports the same four tables used by the current UI; the source EDB
and solver are not modified.
REF docs/source/components/sections/library_excel.py.md
"""
from __future__ import annotations

import argparse
from pathlib import Path
from components.sections.library_excel import export_material_section_library


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export material/section source and citation tables to Excel")
    parser.add_argument("export_dir", type=Path, help="Selected completed ETABS-to-OpenSees export folder")
    args = parser.parse_args(argv)
    if not args.export_dir.is_dir():
        parser.error("Selected ETABS export folder does not exist")
    output = export_material_section_library(args.export_dir)
    print("MATERIAL_SECTION_LIBRARY_XLSX="+str(Path(output).resolve()))
    print("STATUS=EXPORTED_SOURCE_INVENTORY_NOT_NONLINEAR_VALIDATED")
    return output


if __name__ == "__main__":
    main()
