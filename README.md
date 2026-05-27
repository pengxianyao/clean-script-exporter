# Clean Script Exporter

A terminal-based Python tool that packages a local script project into a DLP-safe `.zip` for emailing into a corporate environment (private banking / FI with strict DLP/CS controls).

---

## What it does

1. **Folder picker** — GUI dialog to select your project folder
2. **Dependency report** — scans all `.py` files via AST; splits imports into stdlib (no install needed) and third-party (must be installed on corporate PC)
3. **Missing-file warnings** — detects runtime file references (e.g. `pd.read_excel("data/template.xlsx")`) and warns if they don't exist locally (i.e. the corporate machine must have them)
4. **DLP stripping checklist** — interactive terminal checklist to strip dangerous file types before packaging; preferences saved per-project
5. **Manifest + zip** — prints every file going into the zip, injects a `requirements.txt`, writes `{project-name}-clean-{YYYYMMDD}.zip`

---

## Usage

```bash
python packager.py
```

- A folder picker opens — select your project folder
- Follow the terminal prompts
- Output zip is written to the directory you ran the script from

No external dependencies. Runs on Python 3.10+ (stdlib only).

---

## Default DLP blocklist

The following are stripped by default (toggleable):

`.pyc` · `__pycache__/` · `.exe` · `.dll` · `.db` · `.log` · `.env` · `.DS_Store`

Preferences are saved to `packager-config.json` inside the project folder and reloaded on the next run.

---

## Running tests

```bash
python test_packager.py
```

Tests cover `ImportAnalyser` (stdlib/third-party split, deduplication, syntax error handling) and `FileTracer` (reachable file inclusion, data file detection, missing-file warnings).

---

## Project structure

```
packager.py           # single-file tool — run this
test_packager.py      # tests for ImportAnalyser and FileTracer
PRD.md                # product requirements document
issues/               # implementation issue tickets
CLAUDE.md             # agent config
```

---

## Background

Scripts are developed locally against simulated data and need to be transferred into a corporate environment that enforces DLP/CS policies. The current process is ad hoc — no structured dependency declaration, no repeatable checklist for stripping sensitive file types. This tool makes every transfer repeatable and compliant.
