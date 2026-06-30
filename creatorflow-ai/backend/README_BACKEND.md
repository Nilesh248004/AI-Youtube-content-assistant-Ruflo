# CreatorFlow AI Backend

FastAPI service for the CreatorFlow AI MVP. The API runs a Ruflo-inspired
pipeline of specialist agents with dummy, OpenAI, and Ollama providers.

## Run locally

```bash
cd creatorflow-ai/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for the interactive API documentation.

## LLM providers

Set `LLM_PROVIDER=dummy`, `LLM_PROVIDER=openai`, or `LLM_PROVIDER=ollama` in
`.env`. The template documents provider credentials, model names, timeouts,
retries, logging, and CORS settings.

All specialist agents call `call_llm(prompt: str) -> str` in `llm_client.py`.
Provider output is validated with the Pydantic models in `schemas.py` before it
enters shared workflow state.

## Workflow

```text
Topic → Title → Script → Thumbnail → SEO → Shorts → Review → Final Response
```

`orchestrator.py` acts as the Ruflo-style coordinator. Its in-memory `state`
dictionary acts as the MVP shared workflow ledger. No state persists between
requests.

## Tests

```bash
pip install -r requirements-dev.txt
LLM_PROVIDER=dummy python -m pytest tests -q
```
