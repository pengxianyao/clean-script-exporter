import sys
import tempfile
from pathlib import Path

# Add project root to path so we can import packager
sys.path.insert(0, str(Path(__file__).parent))

from packager import (
    analyse_imports,
    build_entrypoints_text,
    collect_runtime_py_files,
    collect_safe_root_files,
    detect_entrypoints,
    trace_files,
)


def write(tmp: Path, rel: str, content: str) -> Path:
    p = tmp / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


# ── ImportAnalyser tests ──────────────────────────────────────────────────────

def test_splits_stdlib_and_third_party():
    with tempfile.TemporaryDirectory() as d:
        f = write(Path(d), "main.py", "import os\nimport pandas\n")
        result = analyse_imports([f])
        assert "os" in result["stdlib"]
        assert "pandas" in result["third_party"]


def test_handles_from_import():
    with tempfile.TemporaryDirectory() as d:
        f = write(Path(d), "main.py", "from openpyxl import load_workbook\nfrom pathlib import Path\n")
        result = analyse_imports([f])
        assert "openpyxl" in result["third_party"]
        assert "pathlib" in result["stdlib"]


def test_deduplicates_across_files():
    with tempfile.TemporaryDirectory() as d:
        f1 = write(Path(d), "a.py", "import pandas\nimport os\n")
        f2 = write(Path(d), "b.py", "import pandas\nimport sys\n")
        result = analyse_imports([f1, f2])
        assert result["third_party"].count("pandas") == 1
        assert result["stdlib"].count("os") == 1


def test_skips_syntax_errors_gracefully():
    with tempfile.TemporaryDirectory() as d:
        good = write(Path(d), "good.py", "import pandas\n")
        bad = write(Path(d), "bad.py", "def broken(\n")
        result = analyse_imports([good, bad])
        assert "pandas" in result["third_party"]  # good file still processed


def test_empty_file_returns_empty():
    with tempfile.TemporaryDirectory() as d:
        f = write(Path(d), "empty.py", "")
        result = analyse_imports([f])
        assert result["stdlib"] == []
        assert result["third_party"] == []


def test_local_package_import_not_third_party():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        write(root, "profiler/__init__.py", "")
        f = write(root, "profiler/__main__.py", "from profiler.column_profiler import profile_columns\n")
        write(root, "profiler/column_profiler.py", "def profile_columns(): pass\n")
        result = analyse_imports([f], root)
        assert "profiler" not in result["third_party"]


def test_runtime_py_files_exclude_tests():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        main = write(root, "profiler/__main__.py", "")
        test_file = write(root, "tests/test_profiler.py", "import pytest\n")
        files = collect_runtime_py_files(root)
        assert main in files
        assert test_file not in files


# ── FileTracer tests ──────────────────────────────────────────────────────────

def test_includes_all_py_files():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        main = write(root, "main.py", "import helper\n")
        helper = write(root, "helper.py", "x = 1\n")
        result = trace_files(root, [main, helper])
        assert main in result["include"]
        assert helper in result["include"]


def test_includes_referenced_data_file_that_exists():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        template = write(root, "template.xlsx", "fake")
        script = write(root, "main.py", 'import pandas as pd\npd.read_excel("template.xlsx")\n')
        result = trace_files(root, [script])
        assert template in result["include"]


def test_warns_on_missing_referenced_file():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        script = write(root, "main.py", 'open("C:/corporate/report.xlsx")\n')
        result = trace_files(root, [script])
        assert any("report.xlsx" in w for w in result["warnings"])


def test_no_false_positives_from_non_path_strings():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        script = write(root, "main.py", 'x = "hello world"\ny = "SELECT * FROM table"\n')
        result = trace_files(root, [script])
        assert result["warnings"] == []


def test_included_data_file_not_in_warnings():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        write(root, "data.csv", "a,b\n1,2\n")
        script = write(root, "main.py", 'open("data.csv")\n')
        result = trace_files(root, [script])
        assert result["warnings"] == []


def test_collect_safe_root_files_includes_docs_not_bat_runner():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        runner = write(root, "run.bat", "@echo off\n")
        readme = write(root, "README.md", "# App\n")
        write(root, "notes.txt", "ignore me\n")
        files = collect_safe_root_files(root)
        assert runner not in files
        assert readme in files
        assert root / "notes.txt" not in files


def test_detects_package_module_entrypoint():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        main = write(root, "profiler/__main__.py", "def main(): pass\n")
        entrypoints = detect_entrypoints(root, [main])
        assert entrypoints == [{
            "kind": "module",
            "path": "profiler/__main__.py",
            "command": "python -m profiler",
        }]


def test_detects_script_main_guard_entrypoint():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        script = write(root, "packager.py", 'if __name__ == "__main__":\n    main()\n')
        entrypoints = detect_entrypoints(root, [script])
        assert entrypoints == [{
            "kind": "script",
            "path": "packager.py",
            "command": "python packager.py",
        }]


def test_build_entrypoints_text_lists_commands():
    text = build_entrypoints_text([{
        "kind": "module",
        "path": "profiler/__main__.py",
        "command": "python -m profiler",
    }])
    assert "python -m profiler" in text
    assert "profiler/__main__.py" in text


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
