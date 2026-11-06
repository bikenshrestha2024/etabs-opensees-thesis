"""NBC 105:2025 source-input synchronization (OpenSees-first, ETABS fallback).

Run from Spyder with parameters in run configuration, or from a console:
  python 22_NBC105_INPUT_SYNC.py --export "D:\\Thesis Opensees\\Current ETABS Export" --state ULS
  python 22_NBC105_INPUT_SYNC.py --export "..." --state ULS --template "NBC Calculator.xlsx" --etabs-fallback

Always creates a new Excel audit copy; never modifies EDB, source workbook
or ETABS response-spectrum scaling. Source-specific wall indices require review.
"""
from components.inputs.opensees_nbc_sync import main

if __name__=="__main__":
    main()
