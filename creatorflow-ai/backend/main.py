import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from logging_config import configure_logging
from orchestrator import CreatorFlowOrchestrator
from schemas import (
    GenerateRequest,
    GenerateResponse,
    RegeneratableSection,
    RegenerateRequest,
)

load_dotenv()
configure_logging()
logger = logging.getLogger("creatorflow.api")


def _cors_origins() -> list[str]:
    configured = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


def _provider_name() -> str:
    return os.getenv("LLM_PROVIDER", "dummy").strip().lower()


app = FastAPI(
    title="CreatorFlow AI API",
    description="Ruflo-inspired multi-agent YouTube content generation API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = CreatorFlowOrchestrator()


@app.get("/")
def root() -> dict:
    provider = _provider_name()
    return {
        "name": "CreatorFlow AI",
        "status": "ready",
        "docs": "/docs",
        "provider": provider,
        "requires_api_key": provider == "openai",
    }


def _raise_safe_http_error(exc: Exception, operation: str) -> None:
    if isinstance(exc, RuntimeError):
        logger.exception("%s_provider_unavailable", operation)
        raise HTTPException(
            status_code=503,
            detail="The configured LLM provider is unavailable. Check the backend logs.",
        ) from exc

    if isinstance(exc, ValueError):
        logger.exception("%s_validation_failed", operation)
        raise HTTPException(
            status_code=502,
            detail="Generated content did not match the required response format.",
        ) from exc

    logger.exception("%s_failed", operation)
    raise HTTPException(
        status_code=500,
        detail="Content generation failed. Please try again.",
    ) from exc


@app.post("/generate", response_model=GenerateResponse)
def generate_content(request: GenerateRequest) -> dict:
    logger.info("generation_started provider=%s", _provider_name())
    try:
        result = orchestrator.generate(request.model_dump())
    except Exception as exc:
        _raise_safe_http_error(exc, "generation")

    logger.info("generation_completed provider=%s", _provider_name())
    return result


@app.post(
    "/regenerate/{section}",
    response_model=GenerateResponse,
)
def regenerate_content(
    section: RegeneratableSection,
    request: RegenerateRequest,
) -> dict:
    logger.info(
        "regeneration_started provider=%s section=%s",
        _provider_name(),
        section,
    )
    try:
        result = orchestrator.regenerate(
            section,
            request.current_package.model_dump(),
        )
    except Exception as exc:
        _raise_safe_http_error(exc, "regeneration")

    logger.info(
        "regeneration_completed provider=%s section=%s",
        _provider_name(),
        section,
    )
    return result
