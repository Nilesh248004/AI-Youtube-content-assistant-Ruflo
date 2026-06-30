# CreatorFlow AI Backend

FastAPI service for the CreatorFlow AI MVP. The API runs a deterministic,
Ruflo-inspired pipeline of specialist agents and does not require an API key.

## Run locally

```bash
cd creatorflow-ai/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for the interactive API documentation.

## LLM provider integration

All specialist agents call `call_llm(prompt: str) -> str` in `llm_client.py`.
Replace that function with an OpenAI, Gemini, Groq, or Ollama request and return
valid JSON matching each agent's existing output contract. The orchestrator and
API routes do not need to change.

## Workflow

```text
Topic → Title → Script → Thumbnail → SEO → Shorts → Review → Final Response
```

`orchestrator.py` acts as the Ruflo-style coordinator. Its in-memory `state`
dictionary acts as the MVP shared workflow ledger. No state persists between
requests.
