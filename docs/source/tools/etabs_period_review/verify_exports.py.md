# Native ETABS period readback

The [verifier](../../../../tools/etabs_period_review/verify_exports.py) reads paired ETABS assignment and analysis XLSX files and hashes them. It verifies centered linear-static P-Delta steps, story masses and the empirical-reference coefficient, exponent and shear. Once they match, it evaluates NBC Eq. 5.1(1) on signed kN and m floor rows. It writes JSON evidence. [Workflow](../../../../tools/etabs_period_review/README.md)
