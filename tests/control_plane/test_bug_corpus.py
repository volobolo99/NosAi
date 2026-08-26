from app.control_plane.bug_corpus import build_bug_example, build_corpus, sanitize


def test_sanitize_redacts_common_secrets() -> None:
    text = "api_key='sk-test_123456789012345' bearer abcdefgh"
    value = sanitize(text)
    assert "sk-test" not in value
    assert "bearer abcdefgh" not in value.lower()
    assert "[REDACTED]" in value


def test_query_and_ground_truth_are_separate() -> None:
    example = build_bug_example(
        example_id="bug-001",
        repository_id="nosai",
        project_id="control-plane",
        error_signature="TypeError: missing argument",
        stack_trace="runner.py:42",
        affected_files=["app/runner.py"],
        failed_tests=["test_runner"],
        root_cause="caller omitted the context argument",
        patch_summary="pass context explicitly",
        lesson="validate required execution context",
    )
    assert "missing argument" in example.query
    assert all(item not in example.query for item in example.relevant_documents)


def test_corpus_is_stable_and_deduplicated() -> None:
    a = build_bug_example(
        example_id="b-002", repository_id="r", project_id="p", error_signature="A"
    )
    b = build_bug_example(
        example_id="b-001", repository_id="r", project_id="p", error_signature="B"
    )
    result = build_corpus([a, b, a])
    assert [item.example_id for item in result] == ["b-001", "b-002"]
