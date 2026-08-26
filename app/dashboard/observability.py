"""Repository-level test observability and code communication map."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXCLUDED = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache"}
SOURCE_ROOTS = ("app", "tests")
FORBIDDEN_AI_CALLS = {"execute_action", "send_input", "press_key", "click"}


def _files() -> list[Path]:
    return [
        p for root in SOURCE_ROOTS for p in (ROOT / root).rglob("*.py")
        if not any(part in EXCLUDED for part in p.parts)
    ]


def _module_name(path: Path) -> str:
    return path.relative_to(ROOT).with_suffix("").as_posix().replace("/", ".")


def _parse(path: Path) -> tuple[ast.AST | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
        return ast.parse(text, filename=str(path)), None
    except (OSError, SyntaxError, UnicodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def scan_repository() -> dict[str, Any]:
    files = _files()
    records: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    test_files = {p for p in files if "tests" in p.parts}

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree, error = _parse(path)
        rel = path.relative_to(ROOT).as_posix()
        lines = text.splitlines()
        record = {
            "path": rel,
            "module": _module_name(path),
            "bytes": path.stat().st_size,
            "lines": len(lines),
            "nonblank_lines": sum(bool(x.strip()) for x in lines),
            "comment_lines": sum(x.lstrip().startswith("#") for x in lines),
            "sha256_16": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
            "parse": "PASS" if tree is not None else "FAIL",
            "symbols": [],
            "imports": [],
            "calls": [],
            "tests": [],
            "assertions": 0,
            "weight_flags": [],
        }
        if error:
            record["error"] = error
            errors.append({"path": rel, "error": error})
            records.append(record)
            continue
        assert tree is not None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                record["symbols"].append({"name": node.name, "kind": type(node).__name__, "line": node.lineno})
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names]
                record["imports"].extend(names)
                for name in names:
                    edges.append({"from": record["module"], "to": name, "kind": "import"})
            elif isinstance(node, ast.Call):
                func = node.func
                name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else None
                if name:
                    record["calls"].append(name)
            elif isinstance(node, ast.Assert):
                record["assertions"] += 1
        if record["bytes"] > 50000:
            record["weight_flags"].append("OVERSIZED")
        elif record["bytes"] > 20000:
            record["weight_flags"].append("LARGE")
        if record["lines"] and record["comment_lines"] / record["lines"] > 0.35:
            record["weight_flags"].append("COMMENT_HEAVY")
        if "tests" in path.parts:
            record["test_count"] = sum(
                1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")
            )
            if record["test_count"] and record["assertions"] == 0:
                record["weight_flags"].append("NO_ASSERT")
        records.append(record)

    source_files = [r for r in records if r["path"].startswith("app/")]
    for record in source_files:
        stem = Path(record["path"]).stem
        parent = Path(record["path"]).parent.name
        record["tests"] = sorted(
            {
                p.relative_to(ROOT).as_posix()
                for p in test_files
                if stem in p.stem or parent in p.parts
            }
        )

    parsed = sum(r["parse"] == "PASS" for r in records)
    unsafe = [
        r["path"]
        for r in records
        if r["path"].startswith("app/ai/") and FORBIDDEN_AI_CALLS.intersection(r["calls"])
    ]
    gates = {
        "G0": "PASS" if records else "FAIL",
        "G1": "PASS" if records and parsed == len(records) else "FAIL",
        "G2": "NOT_RUN",
        "G3": "PASS" if test_files else "FAIL",
        "G4": "NOT_RUN",
        "G5": "FAIL" if unsafe else "PASS",
        "G6": "WARN" if not (ROOT / "coverage.xml").exists() else "PASS",
    }
    return {
        "root": str(ROOT),
        "files": records,
        "communications": edges,
        "errors": errors,
        "safety_violations": unsafe,
        "gates": gates,
        "summary": {
            "files": len(records),
            "source_files": len(source_files),
            "test_files": len(test_files),
            "parse_failures": len(errors),
            "communication_edges": len(edges),
            "bytes": sum(r["bytes"] for r in records),
            "lines": sum(r["lines"] for r in records),
            "weight_flags": sum(bool(r["weight_flags"]) for r in records),
        },
    }
