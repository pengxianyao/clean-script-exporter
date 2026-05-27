# Issue 4: DLPFilter — Interactive Checklist + Config Persistence

**Type:** AFK  
**Blocked by:** Issue 3  
**Estimated size:** Medium

---

## What to build

Build the `DLPFilter` module and wire it into the main flow after `FileTracer`. The user is shown an interactive checklist of file types/directories to strip before packaging. On first run, the default blocklist is pre-checked. On subsequent runs, saved preferences are loaded from `packager-config.json` in the project folder and pre-applied — the user just presses Enter to accept. Preferences are saved after each run.

Default blocklist: `.pyc`, `__pycache__/`, `.exe`, `.dll`, `.db`, `.log`, `.env`, `.DS_Store`

## Acceptance criteria

- [ ] Interactive checklist is shown in terminal with each type numbered and its current state (strip / keep)
- [ ] User can toggle any item by entering its number; Enter with no input confirms
- [ ] Default blocklist is pre-checked on first run
- [ ] `packager-config.json` is saved to the project folder after the user confirms
- [ ] On subsequent runs, saved preferences are loaded and displayed before prompting
- [ ] Files matching stripped types are excluded from the final zip
- [ ] Directories matching stripped names (e.g. `__pycache__/`) are excluded recursively

## Blocked by

- Issue 3
