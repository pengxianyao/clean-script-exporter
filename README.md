# Clean Script Exporter

Terminal-based Python utility for packaging a local script project into a DLP-conscious zip file that can be shared or moved into a locked-down corporate environment.

## What It Does

- Opens a folder picker so you can choose the project to package.
- Scans Python imports with `ast` and separates standard-library imports from third-party dependencies.
- Traces runtime file references and warns when referenced files are missing.
- Runs an interactive checklist for file types that should be stripped before export.
- Writes a clean zip with a generated `requirements.txt` and a manifest of included files.

## Setup

No third-party packages are required. Use Python 3.10+.

```bash
python --version
```

## Usage

```bash
python packager.py
```

Flow:

1. Select the project folder in the GUI picker.
2. Review dependency and missing-file warnings.
3. Confirm or adjust the DLP stripping checklist.
4. Review the manifest.
5. Use the generated `{project-name}-clean-{YYYYMMDD}.zip`.

## Default DLP Blocklist

The default checklist strips common local, binary, cache, and secret-bearing files:

```text
.pyc
__pycache__/
.exe
.dll
.db
.log
.env
.DS_Store
```

Preferences are saved to `packager-config.json` inside the selected project folder.

## Repository Layout

```text
.
|-- packager.py          # main tool
|-- test_packager.py     # tests
|-- PRD.md               # product requirements
|-- issues/              # implementation tickets
|-- run.bat              # Windows launcher
|-- requirements.txt
`-- README.md
```

## Tests

```bash
python test_packager.py
```

Tests cover dependency detection, syntax-error handling, reachable file tracing, data-file detection, and missing-file warnings.
