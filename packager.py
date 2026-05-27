import ast
import json
import sys
import zipfile
from datetime import date
from pathlib import Path

# ── folder picker ────────────────────────────────────────────────────────────

def pick_folder() -> Path:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select project folder to package")
    root.destroy()
    if not folder:
        print("No folder selected. Exiting.")
        sys.exit(0)
    return Path(folder)


# ── import analyser ──────────────────────────────────────────────────────────

def _stdlib_names() -> set[str]:
    if sys.version_info >= (3, 10):
        return sys.stdlib_module_names  # type: ignore[attr-defined]
    # Fallback for Python < 3.10
    return {
        "abc", "ast", "asyncio", "base64", "builtins", "calendar", "cmath",
        "collections", "contextlib", "copy", "csv", "dataclasses", "datetime",
        "decimal", "difflib", "email", "enum", "fnmatch", "fractions",
        "functools", "gc", "glob", "gzip", "hashlib", "heapq", "html",
        "http", "importlib", "inspect", "io", "itertools", "json", "keyword",
        "linecache", "locale", "logging", "math", "mimetypes", "multiprocessing",
        "operator", "os", "pathlib", "pickle", "platform", "pprint", "queue",
        "random", "re", "shutil", "signal", "socket", "sqlite3", "statistics",
        "string", "struct", "subprocess", "sys", "tempfile", "textwrap",
        "threading", "time", "timeit", "tkinter", "tokenize", "traceback",
        "types", "typing", "unittest", "urllib", "uuid", "warnings",
        "weakref", "xml", "xmlrpc", "zipfile", "zlib",
    }


def analyse_imports(py_files: list[Path]) -> dict[str, list[str]]:
    stdlib = _stdlib_names()
    found: set[str] = set()
    for path in py_files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            print(f"  [warn] Skipping {path.name} — syntax error")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:
                    found.add(node.module.split(".")[0])
    third_party = sorted(m for m in found if m not in stdlib)
    stdlib_used = sorted(m for m in found if m in stdlib)
    return {"stdlib": stdlib_used, "third_party": third_party}


# ── file tracer ──────────────────────────────────────────────────────────────

def _looks_like_path(s: str) -> bool:
    return "." in s and " " not in s and len(s) < 260


def trace_files(root: Path, py_files: list[Path]) -> dict:
    # Pass 1: reachable .py files via local relative imports
    local_modules: dict[str, Path] = {}
    for p in py_files:
        rel = p.relative_to(root)
        module_name = rel.stem
        local_modules[module_name] = p

    reachable: set[Path] = set(py_files)  # all .py files are entry candidates
    warnings: list[str] = []
    include: set[Path] = set(reachable)

    # Pass 2: string literal file references
    for path in py_files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                s = node.value
                if not _looks_like_path(s):
                    continue
                candidate = (root / s).resolve()
                try:
                    candidate.relative_to(root.resolve())
                    if candidate.exists():
                        include.add(candidate)
                    else:
                        warnings.append(s)
                except ValueError:
                    # Path escapes project root — likely a corporate absolute path
                    warnings.append(s)

    return {"include": include, "warnings": warnings}


# ── dlp filter ───────────────────────────────────────────────────────────────

DEFAULT_BLOCKLIST = [".pyc", "__pycache__", ".exe", ".dll", ".db", ".log", ".env", ".DS_Store"]


def _load_config(config_path: Path) -> list[str]:
    if config_path.exists():
        try:
            return json.loads(config_path.read_text())
        except Exception:
            pass
    return DEFAULT_BLOCKLIST[:]


def _save_config(config_path: Path, blocked: list[str]) -> None:
    config_path.write_text(json.dumps(blocked, indent=2))


def apply_dlp_filter(files: set[Path], root: Path, config_path: Path) -> set[Path]:
    blocked = _load_config(config_path)

    print("\n── DLP Stripping Checklist ─────────────────────────────────────")
    if config_path.exists():
        print("  (loaded saved preferences — press Enter to accept)")

    all_types = list(dict.fromkeys(DEFAULT_BLOCKLIST + [b for b in blocked if b not in DEFAULT_BLOCKLIST]))
    state = {t: t in blocked for t in all_types}

    while True:
        for i, t in enumerate(all_types, 1):
            mark = "x" if state[t] else " "
            print(f"  [{mark}] {i}. {t}")
        choice = input("\n  Toggle number (or Enter to confirm): ").strip()
        if not choice:
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(all_types):
                key = all_types[idx]
                state[key] = not state[key]
        except ValueError:
            pass

    blocked = [t for t in all_types if state[t]]
    _save_config(config_path, blocked)

    def is_blocked(path: Path) -> bool:
        for part in path.parts:
            for rule in blocked:
                if rule.startswith(".") and not rule.endswith("/"):
                    if path.suffix == rule or part == rule:
                        return True
                else:
                    if part == rule.rstrip("/"):
                        return True
        return False

    return {f for f in files if not is_blocked(f.relative_to(root) if f.is_relative_to(root) else f)}


# ── packager ─────────────────────────────────────────────────────────────────

def build_zip(files: set[Path], packages: list[str], root: Path, output: Path) -> None:
    sorted_files = sorted(files, key=lambda p: str(p.relative_to(root)))

    print("\n── Manifest ────────────────────────────────────────────────────")
    for f in sorted_files:
        print(f"  {f.relative_to(root)}")
    if packages:
        print("  requirements.txt  (generated)")
    print(f"\n  Total: {len(sorted_files)} file(s)" + (f" + requirements.txt" if packages else ""))

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted_files:
            zf.write(f, f.relative_to(root))
        if packages:
            zf.writestr("requirements.txt", "\n".join(packages) + "\n")

    print(f"\n── Done ────────────────────────────────────────────────────────")
    print(f"  Output: {output}")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    folder = pick_folder()
    print(f"\nProject folder: {folder}")

    py_files = sorted(folder.rglob("*.py"))
    if not py_files:
        print("No .py files found in folder. Exiting.")
        sys.exit(0)

    # Dependency report
    print("\n── Dependency Report ───────────────────────────────────────────")
    report = analyse_imports(py_files)
    print(f"  Stdlib (no install needed): {', '.join(report['stdlib']) or 'none'}")
    print(f"  Third-party (install on corporate PC): {', '.join(report['third_party']) or 'none'}")

    # File tracing
    trace = trace_files(folder, py_files)
    if trace["warnings"]:
        print("\n── Missing File Warnings ───────────────────────────────────────")
        print("  These paths are referenced in code but not found locally.")
        print("  They must exist on the destination machine:")
        for w in sorted(set(trace["warnings"])):
            print(f"  ⚠  {w}")

    # DLP filter
    config_path = folder / "packager-config.json"
    final_files = apply_dlp_filter(trace["include"], folder, config_path)

    # Build zip
    today = date.today().strftime("%Y%m%d")
    output = Path.cwd() / f"{folder.name}-clean-{today}.zip"
    build_zip(final_files, report["third_party"], folder, output)


if __name__ == "__main__":
    main()
