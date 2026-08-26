from __future__ import annotations

import json
import os
from pathlib import Path
from xml.etree import ElementTree


def parse_xml(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"status": "NOT_RUN"}
    try:
        root = ElementTree.parse(path).getroot()
        failures = int(root.attrib.get("failures", 0))
        errors = int(root.attrib.get("errors", 0))
        return {
            "status": "PASS" if failures == 0 and errors == 0 else "FAIL",
            "tests": int(root.attrib.get("tests", 0)),
            "failures": failures,
            "errors": errors,
            "skipped": int(root.attrib.get("skipped", 0)),
            "duration": float(root.attrib.get("time", 0)),
        }
    except (OSError, ValueError, ElementTree.ParseError) as exc:
        return {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}


def parse_coverage(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"status": "NOT_RUN"}
    try:
        root = ElementTree.parse(path).getroot()
        line = float(root.attrib.get("line-rate", 0))
        branch = root.attrib.get("branch-rate")
        return {
            "status": "PASS",
            "line_percent": round(line * 100, 2),
            "branch_percent": round(float(branch) * 100, 2) if branch is not None else None,
        }
    except (OSError, ValueError, ElementTree.ParseError) as exc:
        return {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}


out = Path(os.environ.get("EVIDENCE_OUT", "test-center-evidence.json"))
junit = parse_xml(Path("test-results.xml"))
coverage = parse_coverage(Path("coverage.xml"))
quality = os.environ.get("QUALITY_OUTCOME", "unknown")
static = os.environ.get("STATIC_OUTCOME", "unknown")
cli = os.environ.get("CLI_OUTCOME", "unknown")
run_id = os.environ.get("GITHUB_RUN_ID")
repository = os.environ.get("GITHUB_REPOSITORY")
evidence = {
    "schema": 3,
    "commit": os.environ.get("GITHUB_SHA"),
    "run_id": run_id,
    "workflow": os.environ.get("GITHUB_WORKFLOW"),
    "ref": os.environ.get("GITHUB_REF_NAME"),
    "repository": repository,
    "ci": {
        "status": "PASS" if quality == "success" and static == "success" and cli == "success" else "FAIL",
        "quality": quality,
        "static": static,
        "cli": cli,
        "e2e": "NOT_RUN",
    },
    "junit": junit,
    "coverage": coverage,
    "security": {"status": "NOT_RUN"},
    "sbom": {"status": "NOT_RUN"},
    "artifact": {
        "name": f"nosai-test-center-{os.environ.get('GITHUB_SHA', 'unknown')}",
        "url": f"https://github.com/{repository}/actions/runs/{run_id}" if repository and run_id else None,
    },
}
out.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
