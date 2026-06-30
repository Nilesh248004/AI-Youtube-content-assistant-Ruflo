import json

import pytest
from pydantic import ValidationError

from llm_client import call_llm
from orchestrator import CreatorFlowOrchestrator
from schemas import GenerateRequest, GenerateResponse, ThumbnailOutput


def test_dummy_pipeline_matches_public_response_contract() -> None:
    request = GenerateRequest(topic="Docker vs Kubernetes")
    content = CreatorFlowOrchestrator().generate(request.model_dump())

    validated = GenerateResponse.model_validate(content)
    assert len(validated.workflow.agents_executed) == 8
    assert validated.review.quality_score <= 10


def test_thumbnail_contract_enforces_four_word_limit() -> None:
    with pytest.raises(ValidationError):
        ThumbnailOutput(
            thumbnail_texts=[
                "This thumbnail has too many words",
                "Second title",
                "Third title",
                "Fourth title",
                "Fifth title",
            ]
        )


def test_llm_boundary_rejects_unknown_agent() -> None:
    prompt = json.dumps({"agent": "unknown", "input": {}})

    with pytest.raises(ValueError):
        call_llm(prompt)
