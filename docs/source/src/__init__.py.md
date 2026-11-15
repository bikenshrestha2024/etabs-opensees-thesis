# src/__init__.py — opt-in architecture namespace

Source: `src/__init__.py`. Marks the opt-in `src/` architecture root. This is separate from production `components/`, which still owns existing ETABS-to-OpenSees building workflows. No executable solver, source-model rewrite or analysis acceptance in this package marker. Source tree is covered by the integrated AST audit; runtime compatibility and ETABS/OpenSees equivalence are **NOT_VERIFIED**.
