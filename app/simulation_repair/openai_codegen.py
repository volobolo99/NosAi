"""Optional OpenAI-backed code-candidate generator.

The provider returns structured candidate patches only. It never writes files,
executes generated code, or mutates the repository. Configuration is entirely
environment driven so CI can leave it disabled.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .candidate_generator import CandidateProposal
from .code_generation import CodeCandidate


class CodeGenerationUnavailable(RuntimeError):
    """The configured code-generation service is unavailable or invalid."""


class OpenAICodeGenerationProvider:
    """Generate bounded patch candidates through the Responses API."""

    def __init__(self, *, api_key: str | None = None, model: str | None = None, timeout: float = 45.0) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("NOSAI_CODEGEN_MODEL", "gpt-5.6-luna")
        self.timeout = timeout

    def generate(self, *, error_type: str, message: str, proposals: list[CandidateProposal] | tuple[CandidateProposal, ...]) -> list[CodeCandidate]:
        if not self.api_key:
            raise CodeGenerationUnavailable("OPENAI_API_KEY is not configured")
        compact = [asdict(proposal) for proposal in proposals[:8]]
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "candidate_id": {"type": "string"},
                            "source_candidate_id": {"type": "string"},
                            "file_path": {"type": ["string", "null"]},
                            "patch_text": {"type": "string"},
                            "rationale": {"type": "string"},
                            "evidence_urls": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["candidate_id", "source_candidate_id", "file_path", "patch_text", "rationale", "evidence_urls"],
                    },
                }
            },
            "required": ["candidates"],
        }
        payload = {
            "model": self.model,
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": (
                    "You are a code-research assistant for NosAi. Produce independent "
                    "candidate patches from supplied evidence. Never claim certainty. "
                    "Never include secrets, credentials, destructive commands, or unrelated changes. "
                    "Return small, reviewable unified diffs. Do not execute or apply anything."
                )}]},
                {"role": "user", "content": [{"type": "input_text", "text": json.dumps({
                    "error_type": error_type,
                    "message": message,
                    "research_proposals": compact,
                }, ensure_ascii=False)}]},
            ],
            "text": {"format": {"type": "json_schema", "name": "nosai_code_candidates", "strict": True, "schema": schema}},
        }
        request = Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            raise CodeGenerationUnavailable(f"OpenAI code generation failed: {exc}") from exc

        text = _extract_output_text(body)
        try:
            parsed = json.loads(text)
        except (TypeError, ValueError) as exc:
            raise CodeGenerationUnavailable("OpenAI returned non-JSON structured output") from exc
        candidates: list[CodeCandidate] = []
        for item in parsed.get("candidates", []):
            candidate = CodeCandidate(
                candidate_id=str(item["candidate_id"]),
                source_candidate_id=str(item["source_candidate_id"]),
                file_path=item.get("file_path"),
                patch_text=str(item["patch_text"]),
                rationale=str(item["rationale"]),
                evidence_urls=tuple(str(url) for url in item.get("evidence_urls", [])),
            )
            candidates.append(candidate)
        return candidates


def _extract_output_text(payload: dict) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct
    for item in payload.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str) and text.strip():
                return text
    raise CodeGenerationUnavailable("OpenAI response contained no output text")
