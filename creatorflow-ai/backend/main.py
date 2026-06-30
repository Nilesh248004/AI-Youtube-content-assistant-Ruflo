from typing import Annotated
import traceback

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from orchestrator import CreatorFlowOrchestrator


class GenerateRequest(BaseModel):
    topic: Annotated[str, Field(description="The main YouTube video topic")]
    audience: str = "beginners"
    language: str = "English"
    tone: str = "simple"
    duration: str = "8 minutes"
    goal: str = "educational"

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Topic must not be empty.")
        return cleaned


app = FastAPI(
    title="CreatorFlow AI API",
    description="Ruflo-inspired multi-agent YouTube content generation API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = CreatorFlowOrchestrator()


@app.get("/")
def root() -> dict:
    return {
        "name": "CreatorFlow AI",
        "status": "ready",
        "docs": "/docs",
    }


@app.post("/generate")
def generate_content(request: GenerateRequest) -> dict:
    try:
        print("Received request:", request.model_dump())

        result = orchestrator.generate(request.model_dump())

        print("Content generated successfully")
        return result

    except ValueError as exc:
        print("Validation / ValueError:")
        traceback.print_exc()

        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        print("REAL BACKEND ERROR:")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc