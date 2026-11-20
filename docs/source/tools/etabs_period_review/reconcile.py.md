# ETABS empirical and adopted period calculation

The [review tool](../../../../tools/etabs_period_review/reconcile.py) implements the 95 m ULS case with the reviewed wall geometry. It calculates the preliminary empirical pattern, qualifies automatic P-Delta readback, and accepts a separate capped manual period or explicit direct override. Forces use kN, displacements m and periods s. Source ETABS input is read-only. Staging writes a new E2K exclusively. [Workflow](../../../../tools/etabs_period_review/README.md)
