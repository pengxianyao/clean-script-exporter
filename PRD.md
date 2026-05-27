# PRD: Script Packager — DLP-Safe Export Tool

**Status:** Ready for implementation  
**Author:** Xianyao  
**Date:** 2026-05-27

---

## Problem Statement

Scripts are developed locally against simulated data and must be manually transferred into a corporate environment (private banking FI) with strict DLP/CS controls. The current process is ad hoc: the developer has no structured way to declare which Python packages the destination machine needs, no repeatable checklist for stripping DLP-sensitive file types, and no guarantee the resulting zip will run without modification on the corporate PC. Every transfer is error-prone and time-consuming.

---

## Solution

A single-file terminal Python app (`packager.py`) that the developer runs on their local machine. It opens a folder picker to select the project, analyses all scripts to produce a dependency report and a list of files to include, walks the user through a DLP stripping checklist, displays a manifest of exactly what will be zipped, and writes a clean `.zip` ready to email. No external dependencies — stdlib only.

---

## User Stories

1. As a developer, I want to select my project folder via a GUI dialog, so that I don't have to type paths manually.
2. As a developer, I want the packager to automatically find all Python files in my project, so that I don't have to enumerate them myself.
3. As a developer, I want the packager to analyse imports across all scripts using static analysis, so that I get an accurate dependency report without having to run the code.
4. As a developer, I want to see which imported modules are part of the Python stdlib, so that I know they require no installation on the corporate PC.
5. As a developer, I want to see which imported modules are third-party packages, so that I know exactly what needs to be installed on the corporate PC before running the scripts.
6. As a developer, I want the dependency report shown in the terminal before packaging, so that I can review it and act on it.
7. As a developer, I want the packager to detect runtime file references (e.g. `pd.read_excel("data/template.xlsx")`) from string literals in the code, so that supporting files are automatically included in the zip.
8. As a developer, I want files that are referenced in the code but don't exist locally to be flagged as warnings, so that I know what the corporate machine must have available independently.
9. As a developer, I want only reachable files to be included in the zip (not stale scratch folders or unused experiments), so that the zip is clean and minimal.
10. As a developer, I want a default DLP stripping checklist pre-populated with known-dangerous file types (`.pyc`, `__pycache__/`, `.exe`, `.dll`, `.db`, `.log`, `.env`, `.DS_Store`), so that the safe choice is the fast choice.
11. As a developer, I want to toggle each file type on or off in the stripping checklist, so that I can adjust for edge cases without losing the defaults.
12. As a developer, I want my DLP stripping preferences saved to `packager-config.json` in the project folder, so that I don't have to re-answer each time I repackage.
13. As a developer, I want the saved config to be shown and pre-applied on subsequent runs, so that re-packaging is a single Enter keypress for the common case.
14. As a developer, I want a `requirements.txt` generated and included inside the zip, so that the person on the corporate end has a clear install checklist even if pip cannot be run automatically.
15. As a developer, I want to see a full manifest of every file going into the zip before it is written, so that I can catch mistakes before sending.
16. As a developer, I want the output zip named `{project-folder-name}-clean-{YYYYMMDD}.zip` and written to the directory I ran the packager from, so that it is easy to find and identify.
17. As a developer, I want the entire packager to be a single `.py` file with no external dependencies, so that I can run it anywhere Python is installed without setup.
18. As a developer, I want the terminal output to be clear and structured (dependency report → warnings → file list → DLP checklist → manifest → done), so that I can follow along and catch issues at each stage.
19. As a developer, I want to handle projects with multiple independent entry scripts (e.g. four separate `.py` scripts with shared supporting files), so that all entry points and their shared dependencies are captured in one zip.

---

## Implementation Decisions

### Module: `ImportAnalyser`
- Accepts a list of `.py` file paths.
- Uses `ast.parse` to walk all `import` and `from ... import` statements across every file.
- Splits results into `stdlib` and `third_party` using `sys.stdlib_module_names` (Python 3.10+); falls back to a bundled list for older Python.
- Returns `{ "stdlib": [...], "third_party": [...] }` — sorted, deduplicated.
- Interface is a single function: `analyse_imports(py_files: list[Path]) -> ImportReport`.

### Module: `FileTracer`
- Accepts the project folder root and the full list of `.py` files found in it.
- Determines the inclusion set in two passes:
  - **Pass 1 (Python files):** Walk `ast` for local relative imports to find which `.py` files are reachable from any entry point. All `.py` files that import each other transitively are included.
  - **Pass 2 (data/support files):** Scan all string literals in all `.py` files for values that look like file paths. For each candidate, check if the file exists relative to the project root — if yes, include it; if no, add it to the warnings list.
- Returns `{ "include": set[Path], "warnings": list[str] }`.
- Interface: `trace_files(root: Path, py_files: list[Path]) -> TraceResult`.

### Module: `DLPFilter`
- Accepts a candidate file set and a config path (`packager-config.json` in the project folder).
- Default blocklist: `.pyc`, `__pycache__/`, `.exe`, `.dll`, `.db`, `.log`, `.env`, `.DS_Store`.
- On first run: presents an interactive checklist (each type shown with a checkbox, pre-checked). User toggles by entering the item number; confirms with Enter.
- On subsequent runs: loads saved preferences, displays them, allows editing, confirms with Enter.
- Saves accepted preferences back to `packager-config.json`.
- Returns the filtered file set after applying the confirmed stripping rules.
- Interface: `apply_dlp_filter(files: set[Path], config_path: Path) -> set[Path]`.

### Module: `Packager`
- Accepts the final file set, the third-party package list, the project root, and the output path.
- Generates `requirements.txt` content from the third-party list.
- Prints the full manifest to terminal (each file path, plus `requirements.txt`).
- Writes the zip using `zipfile.ZipFile`, preserving relative paths from the project root.
- Injects `requirements.txt` as a virtual file in the zip root.
- Interface: `build_zip(files: set[Path], packages: list[str], root: Path, output: Path) -> None`.

### Orchestration (`main`)
1. Open `tkinter.filedialog.askdirectory()` to select project folder.
2. Glob all `.py` files in the folder recursively.
3. Run `ImportAnalyser` → print dependency report (stdlib / third-party / warnings).
4. Run `FileTracer` → print missing-file warnings.
5. Run `DLPFilter` → interactive checklist.
6. Print manifest.
7. Run `Packager` → write zip → print output path.

### Output naming
- `{project-folder-name}-clean-{YYYYMMDD}.zip`
- Written to the current working directory (where the packager script is run from).

### Config file
- `packager-config.json` lives in the project folder being packaged.
- Stores the list of stripped extensions/directories as a JSON array.

---

## Testing Decisions

**What makes a good test here:** Test the external behaviour of each module through its public interface only. Do not test internal AST walking or file system calls directly — pass in real (temp) files and assert on the returned data structures. Tests should be fast and runnable with no corporate environment.

### `ImportAnalyser` — tested
- Given a `.py` file importing `pandas` and `os`, returns `pandas` in `third_party` and `os` in `stdlib`.
- Given a file with `from openpyxl import load_workbook`, returns `openpyxl` in `third_party`.
- Given multiple files with overlapping imports, deduplicates correctly.
- Handles syntax errors in source files gracefully (skip file, don't crash).

### `FileTracer` — tested
- Given a folder with `main.py` importing `helper.py`, both are included; `scratch.py` (unreachable) is not.
- Given a string literal `"data/template.xlsx"` and that file existing, it is in the include set.
- Given a string literal `"C:/corporate/report.xlsx"` that doesn't exist locally, it appears in warnings.
- Given no string literals that look like paths, warnings list is empty.

### `DLPFilter` — not independently tested (I/O-heavy; verified manually)

### `Packager` — not independently tested (verified by inspecting output zip)

---

## Out of Scope

- Auto-installing packages on the corporate PC.
- Network calls or corporate system integration.
- Encrypting the zip.
- Supporting `.tar.gz` or any format other than `.zip`.
- A full GUI — only the folder picker is GUI; all interaction is terminal.
- Handling obfuscated or dynamically constructed import strings (e.g. `__import__(var)`).
- Version pinning in `requirements.txt` (package names only, no versions).

---

## Further Notes

- The packager is itself a single `.py` file with zero external dependencies, making it trivially portable.
- `tkinter` is stdlib but occasionally missing on minimal Linux installs; on Windows (the primary target) it is always available.
- The stdlib reference list fallback (for Python < 3.10) should be a hardcoded set of the most common stdlib module names, not a full exhaustive list — good enough for the use case.
- String literal path detection will have false positives (e.g. SQL strings, format strings). The heuristic should require the string to contain a `.` (suggesting a filename) and not contain spaces, to reduce noise.
