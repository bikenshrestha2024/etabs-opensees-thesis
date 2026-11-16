# MESH_04 connectivity and ETABS 23 verification — public index

**Status: SOURCE CONNECTIVITY AUDITED; ETABS–OpenSees NATIVE EQUIVALENCE NOT VERIFIED.**

- [ETABS 23 benchmark review](ETABS23_Analysis_Verification.md)
- [Privacy and engineering acceptance review](../../20261116_PUBLIC_MODEL_EVIDENCE_EXPOSURE_AND_ACCEPTANCE.md)

The converter-generated MESH_04 audit identified two internal frame–slab interface locations (solver node tags 3751 and 3754) where adjacent beam segments and floor cells share the same assembled node tag. This supports direct connectivity *in that particular assembled OpenSees export*, but does not establish identical ETABS native analysis mesh or 32-support reactions.

Four **model-derived** diagnostic exports (two interactive HTML viewers, a node-incidence CSV and a frame/shell JSON) have been removed from the public branch because they contain detailed structural coordinates, sections and topology. The original blobs remain in Git history unless a separate history rewrite is undertaken; do not reintroduce those artifacts into a public branch or automated release.

Future runs should retain those files within the selected **private local ETABS export case's REVIEW** folder and publish only redacted summaries without identifying project coordinates, source locations, node-by-node connectivity or detailed sections. Source identity and numerical engineering evidence belong in private local review packages.

Engineered acceptance sequence: documentation → static topology audit → native ETABS mesh/forces → OpenSees solver tests → MESH_04/08/16 convergence → matched 32-foundation reactions and 6-DOF equilibrium. **No solver equivalence is claimed.**
