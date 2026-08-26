from app.control_plane.repository_intelligence import (
    DeterministicRepositoryRetriever,
    build_index,
    extract_symbols,
    retrieve_repository_context,
)


def test_extract_python_symbols_without_execution() -> None:
    content = "class AgentRunner:\n    def execute_task(self):\n        pass\n"
    assert extract_symbols("app/agent.py", content) == ("AgentRunner", "execute_task")


def test_build_index_is_deterministic() -> None:
    files = {
        "app/agent.py": "def execute_task():\n    pass\n",
        "README.md": "agent documentation",
    }
    assert build_index(files) == build_index(files)


def test_retrieval_prefers_path_and_symbol_matches() -> None:
    files = {
        "app/agent_runner.py": "def execute_task():\n    pass\n",
        "app/database.py": "def execute_query():\n    pass\n",
        "tests/test_agent_runner.py": "def test_execute_task():\n    pass\n",
    }
    results = retrieve_repository_context("agent execute task", files, limit=3)
    assert results
    assert results[0].path == "app/agent_runner.py"
    assert "symbol" in results[0].reasons


def test_retriever_adapter_matches_function() -> None:
    files = {"app/runtime.py": "def run_task():\n    pass\n"}
    adapter = DeterministicRepositoryRetriever()
    assert adapter.retrieve("runtime task", files)[0].path == "app/runtime.py"
