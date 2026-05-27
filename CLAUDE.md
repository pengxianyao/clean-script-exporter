# CLAUDE.md

This file is read by Claude at the start of every session. Keep it short — every token here costs smart-zone budget.

---

## Project

**Name:** Clean Script Exporter (Script Packager)  
**Stack:** Python 3.10+, stdlib only  
**Test runner:** `python test_packager.py` (built-in runner, no framework)  
**Package manager:** none

---

## Key commands

```bash
python packager.py        # run the packager (opens folder picker)
python test_packager.py   # run tests
```

---

## Module map

| Module | Responsibility | Key interface |
|--------|----------------|---------------|
| `analyse_imports(py_files)` | AST-based import scan; splits stdlib vs third-party | `-> {"stdlib": [...], "third_party": [...]}` |
| `trace_files(root, py_files)` | Finds reachable files + string-literal data references; warns on missing | `-> {"include": set[Path], "warnings": [...]}` |
| `apply_dlp_filter(files, root, config_path)` | Interactive DLP checklist; loads/saves `packager-config.json` | `-> set[Path]` |
| `build_zip(files, packages, root, output)` | Prints manifest; writes zip with injected `requirements.txt` | `-> None` |
| `main()` | Orchestrates folder picker → analyse → trace → filter → zip | — |

---

## Coding standards

- Stdlib only — no external dependencies in `packager.py`
- Prefer deep modules over shallow ones (see: A Philosophy of Software Design)
- Tests test external behaviour through the public interface only — no mocking internals
- `packager-config.json` is per-project (lives in the packaged folder, not globally)

---

## Skills available

| Skill | When to use |
|-------|-------------|
| `/grill-me` | Start of any new feature — reach shared understanding |
| `/to-prd` | After grilling — create the destination document |
| `/to-issues` | After PRD — break into vertical-slice tickets |
| `/improve-codebase-architecture` | When agent output quality degrades — deepen modules |

---

## What NOT to do

- Do not read old closed issues as current requirements
- Do not add features outside the current issue scope
- Do not compact — clear context instead and start fresh
- Do not produce a plan when asked to grill — alignment first
- Do not add external dependencies to `packager.py`
