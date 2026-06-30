"""Validated API and agent contracts for CreatorFlow AI."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GenerateRequest(StrictModel):
    topic: str = Field(description="The main YouTube video topic", max_length=200)
    audience: str = Field(default="beginners", max_length=100)
    language: str = Field(default="English", max_length=50)
    tone: str = Field(default="simple", max_length=50)
    duration: str = Field(default="8 minutes", max_length=30)
    goal: str = Field(default="educational", max_length=100)

    @field_validator("*")
    @classmethod
    def text_must_not_be_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Input fields must not be empty.")
        return cleaned


class TopicAnalysis(StrictModel):
    summary: str = Field(min_length=1)
    recommended_angle: str = Field(min_length=1)
    audience_needs: list[str] = Field(min_length=3)
    key_points: list[str] = Field(min_length=5)


class TitleOutput(StrictModel):
    titles: list[str] = Field(min_length=5, max_length=5)


class ScriptSection(StrictModel):
    heading: str = Field(min_length=1)
    content: str = Field(min_length=1)


class ScriptOutput(StrictModel):
    estimated_duration: str = Field(min_length=1)
    target_word_count: int = Field(gt=0)
    hook: str = Field(min_length=1)
    introduction: str = Field(min_length=1)
    main_explanation: list[ScriptSection] = Field(min_length=4)
    real_life_example: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    call_to_action: str = Field(min_length=1)


class ThumbnailOutput(StrictModel):
    thumbnail_texts: list[str] = Field(min_length=5, max_length=5)

    @field_validator("thumbnail_texts")
    @classmethod
    def enforce_thumbnail_word_limit(cls, values: list[str]) -> list[str]:
        if any(len(value.split()) > 4 for value in values):
            raise ValueError("Thumbnail text must contain no more than four words.")
        return values


class SeoOutput(StrictModel):
    description: str = Field(min_length=1)
    tags: list[str] = Field(min_length=10, max_length=10)
    hashtags: list[str] = Field(min_length=8, max_length=8)
    pinned_comment: str = Field(min_length=1)


class ShortsOutput(StrictModel):
    thirty_second_script: str = Field(min_length=1)
    sixty_second_script: str = Field(min_length=1)
    instagram_reel_caption: str = Field(min_length=1)
    hashtags: list[str] = Field(min_length=5, max_length=5)


class ReviewOutput(StrictModel):
    quality_score: float = Field(ge=1, le=10)
    strengths: list[str] = Field(min_length=3)
    improvements: list[str] = Field(min_length=3)
    final_recommendation: str = Field(min_length=1)


class WorkflowMetadata(StrictModel):
    style: str
    agents_executed: list[str]
    last_run_agents: list[str]


class GenerateResponse(StrictModel):
    request: GenerateRequest
    topic_analysis: TopicAnalysis
    titles: list[str] = Field(min_length=5, max_length=5)
    script: ScriptOutput
    thumbnail_texts: list[str] = Field(min_length=5, max_length=5)
    seo: SeoOutput
    shorts: ShortsOutput
    review: ReviewOutput
    workflow: WorkflowMetadata


class RegenerateRequest(StrictModel):
    current_package: GenerateResponse


RegeneratableSection = Literal[
    "topic_analysis",
    "titles",
    "script",
    "thumbnail_texts",
    "seo",
    "shorts",
    "review",
]


AGENT_RESPONSE_MODELS: dict[str, type[BaseModel]] = {
    "topic": TopicAnalysis,
    "title": TitleOutput,
    "script": ScriptOutput,
    "thumbnail": ThumbnailOutput,
    "seo": SeoOutput,
    "shorts": ShortsOutput,
    "review": ReviewOutput,
}


def validate_agent_response(agent_name: str, content: str) -> str:
    """Validate provider JSON and return a normalized JSON string."""

    model = AGENT_RESPONSE_MODELS.get(agent_name)
    if model is None:
        raise ValueError(f"Unknown agent name: {agent_name}")

    validated = model.model_validate_json(content)
    return validated.model_dump_json()


def agent_json_schema(agent_name: str) -> dict[str, Any]:
    model = AGENT_RESPONSE_MODELS.get(agent_name)
    if model is None:
        raise ValueError(f"Unknown agent name: {agent_name}")
    return model.model_json_schema()
