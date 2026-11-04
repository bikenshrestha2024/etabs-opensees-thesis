# Matched waveform audit register

See [eight-pair verification report](README.md) and [component hashes and metrics](matched_component_register.csv).

The public repository stores **numeric metadata only**: no original or matched waveform samples. The files were verified from the user's actual 16 matched exports and 16 pre-matching originals in the study context.

**Primary outstanding code checks:** inspect SeismoMatch project/scale logs, reconcile Gorkha's 322.94s export versus 120s original, review Loma Prieta 0.005s end difference, and recalculate the required modal-based fitting interval. The conditional 0.625g target residual is a research diagnostic, not NBC certification.
