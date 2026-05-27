# Issue 2: ImportAnalyser — Dependency Report

**Type:** AFK  
**Blocked by:** Issue 1  
**Estimated size:** Small–Medium

---

## What to build

Build the `ImportAnalyser` module and wire it into the main flow. After the folder is selected, the packager scans all `.py` files using `ast` to find every imported module, then splits them into two lists: stdlib modules (no install needed on corporate PC) and third-party packages (must be installed). The report is printed to the terminal before packaging proceeds.

## Acceptance criteria

- [ ] All `.py` files in the selected folder are scanned for `import` and `from ... import` statements using `ast`
- [ ] Results are split into `stdlib` and `third_party` lists, sorted and deduplicated
- [ ] Terminal prints both lists clearly before packaging (e.g. "Stdlib: os, sys, pathlib" / "Third-party: pandas, openpyxl")
- [ ] Files with syntax errors are skipped gracefully (warning printed, no crash)
- [ ] Tests cover: stdlib vs third-party split, deduplication across multiple files, graceful syntax error handling

## Blocked by

- Issue 1
