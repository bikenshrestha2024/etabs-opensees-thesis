# `[REF ...]` clause / reference tag convention

Every public function in `components/` (and every function in the new
`tools/plot_results.py` and `tools/export_dashboard.py`) states **where its
engineering rule comes from**, in its docstring, with one or more tags:

```python
def resolve_inherent_damping_ratio(config):
    """Return the inherent damping ratio selected by explicit configuration.

    [REF PEER TBI 2017; LATBSDC 2020] default 0.025.
    [REF NBC105-2025 §8.1.1 (repo citation)] 5% only with an explicit flag.
    """
```

## Syntax

`[REF <source> <locator>]`, matched by the regular expression `\[REF [^\]]+\]`.

| `<source>` form | Example | Use |
|---|---|---|
| Register ID | `R02`, `R10` | Sources listed in [00_RESEARCH_REFERENCES.md](00_RESEARCH_REFERENCES.md) |
| Code + clause | `NBC105-2025 §5.5.3`, `ASCE 41-17 Ch. 10` | Building-code clause. Add `(repo citation)` or `(verify)` when the clause number has not been checked against the official text |
| Author year | `Charney 2008, doi:...` | Papers and books. Give a DOI only when it has been checked |
| OpenSees manual | `OpenSees 'region' command` | Solver command semantics |
| Repo path | `components/sections/definitions.py SECTION_TAGS` | Internal single source of truth; derivation lives elsewhere in the repo |

Rules:

1. A tag records **provenance**, not validation. A cited paper does not
   calibrate this building (see the transfer restrictions in the register).
2. Never invent a clause number, section number or DOI. Write
   `(section number to be verified)` instead.
3. Comments inside a function may carry extra tags at the lines they justify
   (`# [REF ...]`). The test only checks the docstring.

## Enforcement (ratchet)

`tests/verify_ref_tags.py` parses `components/**/*.py` and the two new tools:

* a public (non-underscore) **top-level function or class** without a `[REF`
  tag in its docstring **fails**, unless it is listed in
  `tests/data/ref_tag_baseline.json`;
* the baseline is the frozen list of functions that were untagged on
  2026-11-07 (434 public functions and classes at introduction). It may only **shrink**: if a listed
  function gains a tag, is renamed, or is deleted, the test fails until
  the entry is removed with
  `python tests/verify_ref_tags.py --write-baseline`;
* new modules may not add baseline entries: `--write-baseline` refuses to add
  names that are not already in the baseline.

This lets the existing code be tagged gradually while every new public
function must be tagged from the start.
