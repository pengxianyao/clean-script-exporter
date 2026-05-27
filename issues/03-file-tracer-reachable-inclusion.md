# Issue 3: FileTracer — Reachable-Only Inclusion + Missing-File Warnings

**Type:** AFK  
**Blocked by:** Issue 1  
**Estimated size:** Medium

---

## What to build

Build the `FileTracer` module and wire it into the main flow, replacing the naive "include everything" glob from Issue 1. The tracer determines which files actually need to be in the zip: reachable `.py` files (those transitively imported from any `.py` in the folder) plus data/support files referenced as string literals in the code. Files that are referenced but don't exist locally are flagged as warnings — they are corporate data files the destination machine must provide.

## Acceptance criteria

- [ ] Only `.py` files reachable via local imports from any script in the folder are included; unreachable files (e.g. old experiments) are excluded
- [ ] String literals in `.py` files that look like file paths (contain `.`, no spaces) are checked against the project folder — existing files are included, missing ones are warned
- [ ] Missing-file warnings are printed to the terminal during analysis (not blocking — packaging continues)
- [ ] Non-Python support files (`.md`, `.xlsx`, etc.) referenced in code and present locally are included
- [ ] Tests cover: reachable vs unreachable `.py` files, existing data file inclusion, missing file warning, no false positives from non-path strings

## Blocked by

- Issue 1
