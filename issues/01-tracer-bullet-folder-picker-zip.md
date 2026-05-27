# Issue 1: Tracer Bullet — Folder Picker → Zip

**Type:** AFK  
**Blocked by:** None  
**Estimated size:** Small

---

## What to build

Wire the end-to-end skeleton: a `tkinter` folder picker opens, the user selects a project folder, all files in the folder are globbed recursively, and the result is written as `{folder-name}-clean-{YYYYMMDD}.zip` in the current working directory. No filtering, no analysis, no stripping — just the full pipeline from picker to zip, proving the skeleton runs.

This is the foundation every subsequent issue builds on. Keep it thin.

## Acceptance criteria

- [ ] Running `python packager.py` opens a folder picker dialog
- [ ] After selecting a folder, all files are included in a zip (no filtering yet)
- [ ] Output zip is named `{project-folder-name}-clean-{YYYYMMDD}.zip` and written to cwd
- [ ] Terminal confirms the output path when done
- [ ] Script has zero external dependencies (stdlib only)

## Blocked by

None — can start immediately.
