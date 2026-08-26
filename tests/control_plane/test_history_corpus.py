from pathlib import Path
import subprocess

from app.control_plane.history_corpus import build_history_corpus, collect_git_history


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    run = lambda *args: subprocess.run(args, cwd=repo, check=True, capture_output=True, text=True)
    run("git", "init")
    run("git", "config", "user.email", "nosai@example.invalid")
    run("git", "config", "user.name", "NosAi Test")
    (repo / "bug.py").write_text("broken\n", encoding="utf-8")
    run("git", "add", "bug.py")
    run("git", "commit", "-m", "initial")
    (repo / "bug.py").write_text("fixed\n", encoding="utf-8")
    run("git", "add", "bug.py")
    run("git", "commit", "-m", "fix: repair regression in runner")
    return repo


def test_collect_history_is_read_only(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    records = collect_git_history(str(repo), limit=10)
    assert records
    assert records[0].commit
    assert "fix" in records[0].subject.lower()


def test_build_history_corpus_selects_fix_like_commits(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    corpus = build_history_corpus(str(repo), repository_id="nosai", project_id="control", limit=10)
    assert len(corpus) == 1
    assert corpus[0].repository_id == "nosai"
    assert corpus[0].project_id == "control"
    assert "repair regression" in corpus[0].query
