# -*- coding: utf-8 -*-
"""Spyder entry point for current offline ETABS / OpenSees 32/76/97 gravity audit.

Core implementation lives in components.validation.gravity_etabs_latest.
No ETABS COM, analysis, or changes to model/reactions are performed.
"""
from components.validation.gravity_etabs_latest import main, run

if __name__ == "__main__":
    main()
