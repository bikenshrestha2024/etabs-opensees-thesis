# src/etabs_adapter/__init__.py — optional CSI interface namespace

Source: `src/etabs_adapter/__init__.py`. This package is reserved for optional ETABS-specific adapters. Standalone neutral schema and OpenSees benchmark must not import CSI/COM through this namespace. `bridge.py` lazily exposes existing components; this namespace does not replace the original ETABS exporter. Source-only import boundaries are tested by `tests/verify_etabs_adapter_boundary.py`; native ETABS execution is **NOT_VERIFIED**.
