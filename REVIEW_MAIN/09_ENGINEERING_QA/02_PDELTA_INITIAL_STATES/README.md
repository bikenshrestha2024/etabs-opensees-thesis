# 02 — P-Delta initial states, tangent stiffness and time-history loading

**First read:** [Why signed static ±1.5EL is not automatically a permanent NLTHA load](01_SIGNED_EL_VS_GRAVITY_START.md) — answers nine practical questions with equations, ETABS/OpenSees distinctions, source citations, acceptance gates and reproducible experiment options.

**Q. Are signed initial cases optional?** No: compulsory project prerequisite under IS 16700 §7.2(d), subordinate to NBC 105 seismic basis.

**Q. Do they automatically initialize the nonlinear earthquake state?** No: a verified native gravity-equilibrated state with geometrically nonlinear model response is the recommended production initialization; signed EL bias is a separate, explicitly justified research scenario.

**When:** After source/model/gravity audit, before full XY/YX histories. **Who:** researcher performs, engineering reviewer checks source/transfer and dynamic state.

[P0 parent review](../../00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md) · [Gravity-to-TH handoff](../../07_TIME_HISTORY/20261113_NBC_GRAVITY_PRELOAD_TO_EQ_TRANSIENT_DECISION.md) · [Q&A home](../README.md)

**Status:** intended method; ETABS/OpenSees native state-transfer parity open.
