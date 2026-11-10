# Migration phases 2–7: safe execution status

**Source baseline:** `bikenshrestha2024/opensees-nbc105-research` at `df69ae625c97a971fe7846536123f1141be1d600`. **Destination pre-migration:** `382750021895fd7300f6c912457c1ccbc2a445f9`. No source repo writes.

| Phase | Actual delivery | Safety / remaining gate |
|---|---|---|
| 2 Inventory and separation | Subject-area directories, AST import/duplicate audit and ownership output; active modules retained at existing paths | Runtime/dynamic imports require Windows verification |
| 3 Standalone core | Versioned, deliberately limited neutral schema and ETABS-independent small elastic cantilever benchmark | No 25-storey ETABS-to-neutral mapper yet; no RCC wall/FVD/BRB claim |
| 4 Code consolidation | Existing active modules remain canonical, explicit path mapping and topic navigation | **No deletion** of duplicate saved historical and runtime packages pending dependent-path tests |
| 5 Engineering quality | Existing physical validation gates recorded; no imposed physics or scaling changes | Native ETABS v23 and full building solver tests still required |
| 6 AI optimization | Existing Codex/Claude/Copilot/ChatGPT/DeepSeek rules preserved | Edit attribution voluntary, not forensic evidence |
| 7 Release/handoff | Reversible migration and static tests documented | **NOT a validated numerical release**; do not present full reorganization as scientifically complete |

The existing root and `components/` imports remain stable. Full source relocation would break historical dynamic `exec` facades and generated runtime references if done before all dependencies are identified. This phase deliberately adds discoverability without altering working numerical behavior.
