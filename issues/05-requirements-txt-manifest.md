# Issue 5: requirements.txt Generation + Terminal Manifest

**Type:** AFK  
**Blocked by:** Issues 2 and 4  
**Estimated size:** Small

---

## What to build

Wire the final two output steps: generate a `requirements.txt` from the third-party package list and inject it into the zip, and print a full manifest of every file going into the zip to the terminal before writing. This completes the packager — after this issue, the tool is fully functional end-to-end.

## Acceptance criteria

- [ ] Terminal prints a full manifest (every file path relative to project root, plus `requirements.txt`) before writing the zip
- [ ] `requirements.txt` is included in the zip root listing all third-party packages, one per line
- [ ] `requirements.txt` is not written to disk — injected directly into the zip as a virtual file
- [ ] Manifest is readable and clearly formatted (not a raw dump)
- [ ] After the zip is written, the terminal prints the full output path

## Blocked by

- Issue 2
- Issue 4
