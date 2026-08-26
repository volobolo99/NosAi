"""Repository-level test observability and CI evidence aggregation."""
from __future__ import annotations
import ast, hashlib, json, os, subprocess, urllib.request, zipfile
from io import BytesIO
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
EXCLUDED={".git",".venv","venv","__pycache__",".pytest_cache",".mypy_cache"}
SOURCE_ROOTS=("app","tests")
FORBIDDEN_AI_CALLS={"execute_action","send_input","press_key","click"}
EVIDENCE_DIR=Path(os.getenv("NOSAI_TEST_EVIDENCE_DIR",str(ROOT)))
def _files(): return [p for root in SOURCE_ROOTS for p in (ROOT/root).rglob("*.py") if not any(part in EXCLUDED for part in p.parts)]
def _module_name(path): return path.relative_to(ROOT).with_suffix("").as_posix().replace("/",".")
def _parse(path):
    try:return ast.parse(path.read_text(encoding="utf-8"),filename=str(path)),None
    except (OSError,SyntaxError,UnicodeError) as exc:return None,f"{type(exc).__name__}: {exc}"
def _current_commit():
    try:return subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True,timeout=2).strip()
    except (OSError,subprocess.SubprocessError):return os.getenv("GITHUB_SHA")
def _read_evidence(path):
    if not path.exists():return {"status":"NOT_RUN"}
    try:
        data=json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data,dict):return {"status":"FAIL","error":"evidence is not an object"}
        ec=data.get("commit"); cc=_current_commit()
        if ec and cc and ec!=cc:return {"status":"NOT_RUN","error":"local Test Center evidence is stale for current commit"}
        return data
    except (OSError,ValueError,json.JSONDecodeError) as exc:return {"status":"FAIL","error":f"{type(exc).__name__}: {exc}"}
def _remote_evidence():
    token=os.getenv("NOSAI_GITHUB_TOKEN"); repo=os.getenv("NOSAI_GITHUB_REPOSITORY","volobolo99/NosAi")
    if not token:return {"status":"NOT_RUN","error":"NOSAI_GITHUB_TOKEN not configured"}
    try:
        req=urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/artifacts?per_page=30",headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
        with urllib.request.urlopen(req,timeout=10) as r: listing=json.load(r)
        artifacts=[a for a in listing.get("artifacts",[]) if a.get("name","").startswith("nosai-test-center-") and not a.get("expired")]
        if not artifacts:return {"status":"NOT_RUN","error":"No Test Center artifact found"}
        artifact=max(artifacts,key=lambda a:a.get("created_at",""))
        req=urllib.request.Request(artifact["archive_download_url"],headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
        with urllib.request.urlopen(req,timeout=20) as r: payload=r.read()
        with zipfile.ZipFile(BytesIO(payload)) as z:
            with z.open("test-center-evidence.json") as stream:data=json.load(stream)
        data["source"]="github-artifact";data["artifact"]={"id":artifact.get("id"),"name":artifact.get("name"),"created_at":artifact.get("created_at"),"expired":artifact.get("expired")};return data
    except (OSError,ValueError,KeyError,json.JSONDecodeError,zipfile.BadZipFile) as exc:return {"status":"FAIL","error":f"GitHub evidence fetch: {type(exc).__name__}: {exc}"}
def ci_evidence():
    local=_read_evidence(EVIDENCE_DIR/"test-center-evidence.json")
    return {**local,"source":"local"} if local.get("status")!="NOT_RUN" else _remote_evidence()
def scan_repository():
    files=_files();records=[];edges=[];errors=[];test_files={p for p in files if "tests" in p.parts}
    for path in files:
        text=path.read_text(encoding="utf-8",errors="replace");tree,error=_parse(path);rel=path.relative_to(ROOT).as_posix();lines=text.splitlines()
        record={"path":rel,"module":_module_name(path),"bytes":path.stat().st_size,"lines":len(lines),"nonblank_lines":sum(bool(x.strip()) for x in lines),"comment_lines":sum(x.lstrip().startswith("#") for x in lines),"sha256_16":hashlib.sha256(text.encode()).hexdigest()[:16],"parse":"PASS" if tree is not None else "FAIL","symbols":[],"imports":[],"calls":[],"tests":[],"assertions":0,"weight_flags":[]}
        if error:record["error"]=error;errors.append({"path":rel,"error":error});records.append(record);continue
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):record["symbols"].append({"name":node.name,"kind":type(node).__name__,"line":node.lineno})
            elif isinstance(node,(ast.Import,ast.ImportFrom)):
                names=[a.name for a in node.names];record["imports"].extend(names);edges.extend({"from":record["module"],"to":name,"kind":"import"} for name in names)
            elif isinstance(node,ast.Call):
                name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else None
                if name:record["calls"].append(name)
            elif isinstance(node,ast.Assert):record["assertions"]+=1
        if record["bytes"]>50000:record["weight_flags"].append("OVERSIZED")
        elif record["bytes"]>20000:record["weight_flags"].append("LARGE")
        if record["lines"] and record["comment_lines"]/record["lines"]>.35:record["weight_flags"].append("COMMENT_HEAVY")
        if "tests" in path.parts:
            record["test_count"]=sum(1 for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith("test_"))
            if record["test_count"] and record["assertions"]==0:record["weight_flags"].append("NO_ASSERT")
        records.append(record)
    source_files=[r for r in records if r["path"].startswith("app/")]
    for record in source_files:
        stem=Path(record["path"]).stem;parent=Path(record["path"]).parent.name;record["tests"]=sorted({p.relative_to(ROOT).as_posix() for p in test_files if stem in p.stem or parent in p.parts})
    parsed=sum(r["parse"]=="PASS" for r in records);unsafe=[r["path"] for r in records if r["path"].startswith("app/ai/") and FORBIDDEN_AI_CALLS.intersection(r["calls"])]
    evidence=ci_evidence();junit=evidence.get("junit",{});coverage=evidence.get("coverage",{});ci=evidence.get("ci",{});security=evidence.get("security",{});sbom=evidence.get("sbom",{});has_evidence=evidence.get("status") not in (None,"NOT_RUN")
    static_ok=ci.get("static")=="success";security_ok=security.get("status")=="PASS";sbom_ok=sbom.get("status")=="PASS"
    g2="NOT_RUN" if not has_evidence else ("PASS" if static_ok and security_ok and sbom_ok else "FAIL")
    gates={"G0":"PASS" if records else "FAIL","G1":"PASS" if records and parsed==len(records) else "FAIL","G2":g2,"G3":junit.get("status","NOT_RUN"),"G4":ci.get("e2e","NOT_RUN"),"G5":"FAIL" if unsafe else "PASS","G6":"PASS" if coverage.get("status")=="PASS" else "WARN"}
    return {"root":str(ROOT),"files":records,"communications":edges,"errors":errors,"safety_violations":unsafe,"gates":gates,"ci":ci,"junit":junit,"coverage":coverage,"security":security,"sbom":sbom,"evidence":{k:evidence.get(k) for k in ("source","artifact","commit","run_id","workflow","ref","repository") if k in evidence},"summary":{"files":len(records),"source_files":len(source_files),"test_files":len(test_files),"parse_failures":len(errors),"communication_edges":len(edges),"bytes":sum(r["bytes"] for r in records),"lines":sum(r["lines"] for r in records),"weight_flags":sum(bool(r["weight_flags"]) for r in records)}}
