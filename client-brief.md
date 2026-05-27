# Client Brief

**From:** Xianyao / Julius Baer CDS COO Asia  
**Date:** 2026-05-27  
**Project:** Script Packager — DLP-Safe Export Tool

---

## The Ask

Build a terminal-based Python app ("packager") that takes a locally developed Python script/project folder and packages it into a zip file safe for emailing into a corporate environment (private banking FI) that enforces DLP/CS policies.

The packager must:
- Analyse the target script(s) and report what Python packages the corporate PC will need to have installed
- Interactively ask the user which file types to strip before packaging (e.g. `__pycache__`, `.pyc`, `.db`, `.log`, etc.) since DLP may block certain extensions
- Output a clean `.zip` that is fully runnable on the corporate PC just by unzipping and running `python`

Background: scripts are developed locally against simulated data (modelled on real corporate Excel files), and the packaged output is intended to run against those actual Excel files in the corporate environment.

---

## Context

- **Current situation:** Scripts are built outside the corporate environment and need to be brought in manually. The current process has no structured way to declare dependencies or strip DLP-sensitive files before sending — the developer has to do this ad hoc each time.
- **Why now:** Repeated friction sending scripts into the corporate environment; DLP blocks are unpredictable. A repeatable, checklist-driven packager reduces errors and compliance risk.
- **Success looks like:** Developer runs the packager, sees a clear list of required packages for the corporate PC, approves/denies file-type stripping interactively, and gets a clean `.zip` that passes DLP and runs without modification on the corporate machine.

---

## Constraints

- **Timeline:** ASAP / personal productivity tool
- **Budget / scope:** Single Python script; no external dependencies for the packager itself (stdlib only where possible, or clearly flagged if not)
- **Technical constraints:**
  - Corporate PC runs Python (version parity assumed); no internet access for pip at runtime
  - DLP/CS will likely block: `.pyc`, `__pycache__/`, `.exe`, `.dll`, `.db`, `.log` — `.py` and `.md` are generally safe
  - Packager runs on the developer's local machine (non-corporate), so any packaging deps are fine there
  - Output must be a standard `.zip` (no `.tar.gz` or other formats)
  - Scripts typically depend on `pandas`, `openpyxl`, `matplotlib`, `tkinter` and similar data/GUI libraries
- **Out of scope:**
  - Auto-installing packages on the corporate PC
  - Any network calls or corporate system integration
  - Encrypting the zip

---

## Open Questions

- [ ] Should the packager support multi-file projects (a folder) as well as single `.py` files, or single files only for now?
- [ ] Should the required-packages report distinguish between stdlib modules (no install needed) and third-party packages?
- [ ] Should there be a saved config / profile for DLP stripping preferences so the user doesn't have to re-answer each time?
- [ ] Is a `requirements.txt` to be included in the zip (for documentation), even though pip can't be run on the corporate PC?
