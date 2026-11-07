# AI contribution provenance for the ETABS–OpenSees thesis

Git author/committer metadata is **not proof** of which AI assisted with a change. ChatGPT, Codex, Claude, Claude Code, Copilot, Gemini and Qwen may all push using the same GitHub account. Do not infer attribution from coding style.

## Evidence grades

- `SESSION_OBSERVED`: assistance recorded in a conversation where the assistant made the GitHub commit.
- `COMMIT_DECLARED`: explicit commit trailer or PR description names the assistant/model.
- `USER_ATTESTED`: user identifies assistance and points to its supporting session.
- `UNKNOWN`: no reliable source; never guess.

## Future commit trailers

```text
AI-Assisted-By: ChatGPT | Codex | Claude | Claude Code | GitHub Copilot | Gemini | Qwen | None | Unknown
AI-Model: <exact model if known, otherwise Unknown>
AI-Evidence: <session, issue or pull request URL if available>
Human-Reviewed-By: <name or NOT_REVIEWED>
Engineering-Validation: NOT_RUN | STATIC_TESTS_ONLY | NATIVE_PROJECT_VERIFIED | EXPERIMENTALLY_VALIDATED
```

For collaboration between multiple AI tools, list contributions individually in the pull request description and repeat `AI-Assisted-By` as necessary. Do not rewrite existing commit history to change attribution.

## Historically observed session attribution

The following commits were made through **ChatGPT's connected GitHub integration** in the recorded conversation. This identifies the interaction used to submit them; it does **not** claim that every original engineering idea or source artifact originated with ChatGPT.

| Commit prefix | Change | Source interaction | Grade |
|---|---|---|---|
| bcac359 | ETABS-linked Excel adapter | ChatGPT GitHub connector | SESSION_OBSERVED |
| 80de3ef | ESM GUI integration | ChatGPT GitHub connector | SESSION_OBSERVED |
| 280305a | ESM regression tests | ChatGPT GitHub connector | SESSION_OBSERVED |
| 969d2b6 | ESM integration documentation | ChatGPT GitHub connector | SESSION_OBSERVED |
| b07c943 | Required ESM source guide | ChatGPT GitHub connector | SESSION_OBSERVED |
| 515abc4 | CI ESM tests | ChatGPT GitHub connector | SESSION_OBSERVED |
| caaae21 | Thesis evidence dashboard | ChatGPT GitHub connector | SESSION_OBSERVED |
| 93ce29d | Evidence dashboard tests | ChatGPT GitHub connector | SESSION_OBSERVED |
| aca5595 | Dashboard source guide | ChatGPT GitHub connector | SESSION_OBSERVED |
| a46bcf4 | Elastic C vs design Cd correction | ChatGPT GitHub connector | SESSION_OBSERVED |
| 5ad9a4a | Coefficient regression test | ChatGPT GitHub connector | SESSION_OBSERVED |
| c2289d7 | Dashboard CI integration | ChatGPT GitHub connector | SESSION_OBSERVED |
| 11418bd | Dashboard entry point | ChatGPT GitHub connector | SESSION_OBSERVED |
| 2f58798 | Dashboard user guide | ChatGPT GitHub connector | SESSION_OBSERVED |
| 48336b2 | Canonical workflow index | ChatGPT GitHub connector | SESSION_OBSERVED |
| fa20a12 | Research implementation roadmap | ChatGPT GitHub connector | SESSION_OBSERVED |

All other commits require independent evidence; the GitHub author `bikenshrestha2024` or committer `GitHub` does not resolve which AI was involved.

## Engineering note

An AI provenance label is independent of engineering validation. Numerical stability is not experimental calibration, and neither implies NBC 105:2025 design approval. Preserve input/model hashes and actual native test output alongside these attribution records.
