# Bind exploratory tolerance to each batch job

Editor OpenAI Codex desktop. Base `5fd479a0567058c55a42c7ce97fd74b43eef4e99`. Batch preparation uses the existing exploratory settings validator before hashing inputs. It stores the effective tolerance, iteration limit and final fallback in the job configuration and fingerprint. The Stage 38 runbook documents the strict opt-in. Existing production gates, physical supports and wall mesh points, full-gravity benchmark, NBC seismic weights, motion scaling and solver algorithms retain their source definitions.

The batch regression reproduced missing settings in queued jobs, duplicate effective settings receiving separate fingerprints and invalid tolerance being discovered after model validation. After the change, 74 targeted tests and 14 subtests passed. The native Tk strict-tolerance control initially rendered unchecked and toggled to checked when invoked.

The repository suite also reproduced a Windows test interaction. The gravity test's temporary environment override caused Git to lose an empty configuration value when the helper restored the process environment, so the next review-ledger command failed. The fixture now provides a temporary mapping for the gravity test without rewriting the process environment.

Native OpenSeesPy 3.8.0 verified the local clear-beam export and registered Kobe A/B files and began the full exploratory XY/YX job at `1e-6` and `0.005 s`. At this checkpoint the XY run had accepted finite transient steps. Full-record convergence, ETABS–OpenSees equivalence, experimental validation and code acceptance remain unverified. Native project inputs and outputs remain local.
