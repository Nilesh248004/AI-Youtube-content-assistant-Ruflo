# CreatorFlow AI

CreatorFlow AI is a runnable React + FastAPI MVP that turns one YouTube topic
into a complete content package. It uses a lightweight, Ruflo-inspired
multi-agent workflow with specialist agents for strategy, titles, scripting,
thumbnails, SEO, short-form content, review, and final response assembly.

![CreatorFlow AI interface preview](docs/ui-preview.svg)

No database is required. Choose the deterministic dummy provider, OpenAI, or a
local Ollama model through environment configuration without changing the
agents or orchestration workflow.

## Why Ruflo is useful here

[Ruflo](https://github.com/ruvnet/ruflo) treats an agent system as more than one
large prompt. It provides a harness around specialized agents, coordination,
task state, memory, tools, and review loops. That separation is valuable for a
content workflow because each stage has a different success criterion:

- The Topic Agent optimizes for audience and angle.
- The Title and Thumbnail Agents optimize for accurate discovery.
- The Script Agent optimizes for teaching structure and pacing.
- The SEO and Shorts Agents adapt the core idea for other surfaces.
- The Review Agent acts as a quality gate.
- The Final Response Agent enforces one stable API contract.

The full Ruflo runtime includes a Node CLI, MCP tools, hooks, swarm topologies,
plugins, and persistent vector memory. Pulling that entire runtime into this
no-key Python MVP would add unnecessary setup. CreatorFlow AI therefore
implements the same core boundaries as a small in-process workflow. A future
version can replace the in-process coordinator with Ruflo MCP/task commands
without redesigning the agent responsibilities.

## Ruflo concept mapping

| Ruflo concept | CreatorFlow AI MVP |
|---|---|
| Specialized agent definitions | One Python class per file in `backend/agents/` |
| Swarm coordinator / harness | `CreatorFlowOrchestrator` |
| Shared task ledger / swarm state | Per-request in-memory `state` dictionary |
| Agent handoff | Each result is merged into state for downstream agents |
| Memory | Request-scoped context only; no persistence in the MVP |
| Workflow command | `POST /generate` starts the pipeline |
| Quality / review agent | `ReviewAgent` |
| Structured final output | `FinalResponseAgent` |
| LLM provider routing | Replaceable `call_llm()` boundary |

## Architecture

```text
React + Vite form
       |
       | POST /generate
       v
FastAPI request validation
       |
       v
CreatorFlowOrchestrator
       |
       +--> Topic Agent
       |       |
       +--> Title Agent
       |       |
       +--> Script Agent
       |       |
       +--> Thumbnail Agent
       |       |
       +--> SEO Agent
       |       |
       +--> Shorts Agent
       |       |
       +--> Review Agent
       |       |
       +--> Final Response Agent
               |
               v
       Structured JSON response
               |
               v
       React result cards

Every specialist calls:
agent -> call_llm(prompt) -> structured JSON contribution
```

## Features

- Topic, audience, language, tone, duration, and goal inputs
- Seven specialist generation/review agents plus a final response agent
- Five non-clickbait title ideas
- Structured long-form video script
- Five thumbnail phrases, each no longer than four words
- Description, ten tags, eight hashtags, and pinned comment
- 30-second and 60-second Shorts scripts
- Instagram Reel caption and short-form hashtags
- Quality score, strengths, improvement ideas, and recommendation
- FastAPI validation, CORS, and basic error handling
- Responsive React UI with loading and error states
- Dummy, OpenAI, and Ollama provider support
- Strict Pydantic validation for every agent response
- Configurable provider timeouts, retries, CORS origins, and structured logs
- Copy, JSON export, Markdown export, and targeted section regeneration
- React error boundary and backend request timeouts
- Automated backend tests and GitHub Actions verification

## Folder structure

```text
creatorflow-ai/
├── backend/
│   ├── main.py
│   ├── orchestrator.py
│   ├── llm_client.py
│   ├── schemas.py
│   ├── logging_config.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env.example
│   ├── README_BACKEND.md
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_api.py
│   │   └── test_contracts.py
│   └── agents/
│       ├── __init__.py
│       ├── topic_agent.py
│       ├── title_agent.py
│       ├── script_agent.py
│       ├── thumbnail_agent.py
│       ├── seo_agent.py
│       ├── shorts_agent.py
│       ├── review_agent.py
│       └── final_response_agent.py
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── .env.example
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── ErrorBoundary.jsx
│       ├── api.js
│       ├── exportUtils.js
│       └── App.css
├── docs/
│   └── ui-preview.svg
├── .gitignore
└── README.md
```

## Backend setup

From the directory that contains `creatorflow-ai`:

```bash
cd creatorflow-ai/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

The API is available at `http://localhost:8000` and the interactive docs are at
`http://localhost:8000/docs`.

## Frontend setup

Open a second terminal:

```bash
cd creatorflow-ai/frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

The frontend calls `http://localhost:8000/generate` by default. To use another
backend URL, copy `frontend/.env.example` to `frontend/.env` and update
`VITE_API_URL`.

## API

### Health / service information

```http
GET /
```

### Generate a content package

```http
POST /generate
Content-Type: application/json
```

Example with curl:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Docker vs Kubernetes",
    "audience": "Beginners",
    "language": "English",
    "tone": "Simple",
    "duration": "8 minutes",
    "goal": "Educational video"
  }'
```

Only `topic` is required. The server uses these defaults for omitted fields:

```json
{
  "audience": "beginners",
  "language": "English",
  "tone": "simple",
  "duration": "8 minutes",
  "goal": "educational"
}
```

An empty or whitespace-only topic returns HTTP `422`.

### Regenerate one section

```http
POST /regenerate/{section}
Content-Type: application/json
```

Supported sections are `topic_analysis`, `titles`, `script`,
`thumbnail_texts`, `seo`, `shorts`, and `review`. Send the current package as:

```json
{
  "current_package": {
    "...": "the complete response from POST /generate"
  }
}
```

The selected agent and all downstream agents run again. Upstream content stays
unchanged, which preserves the workflow's dependency order.

## Sample response format

```json
{
  "request": {
    "topic": "Docker vs Kubernetes",
    "audience": "Beginners",
    "language": "English",
    "tone": "Simple",
    "duration": "8 minutes",
    "goal": "Educational video"
  },
  "topic_analysis": {
    "summary": "...",
    "recommended_angle": "...",
    "audience_needs": ["..."],
    "key_points": ["..."]
  },
  "titles": ["...", "...", "...", "...", "..."],
  "script": {
    "estimated_duration": "8 minutes",
    "target_word_count": 1040,
    "hook": "...",
    "introduction": "...",
    "main_explanation": [
      {
        "heading": "...",
        "content": "..."
      }
    ],
    "real_life_example": "...",
    "summary": "...",
    "call_to_action": "..."
  },
  "thumbnail_texts": ["...", "...", "...", "...", "..."],
  "seo": {
    "description": "...",
    "tags": ["10 values"],
    "hashtags": ["8 values"],
    "pinned_comment": "..."
  },
  "shorts": {
    "thirty_second_script": "...",
    "sixty_second_script": "...",
    "instagram_reel_caption": "...",
    "hashtags": ["..."]
  },
  "review": {
    "quality_score": 8.7,
    "strengths": ["..."],
    "improvements": ["..."],
    "final_recommendation": "..."
  },
  "workflow": {
    "style": "Ruflo-inspired sequential multi-agent orchestration",
    "agents_executed": ["topic_agent", "...", "final_response_agent"],
    "last_run_agents": ["topic_agent", "...", "final_response_agent"]
  }
}
```

## LLM provider configuration

Copy the environment template:

```bash
cd backend
cp .env.example .env
```

Use one of these provider values:

```dotenv
# Deterministic local demo; no API key or model download
LLM_PROVIDER=dummy

# OpenAI structured outputs
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4.1-mini

# Local Ollama
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
OLLAMA_HOST=http://localhost:11434
```

Provider calls use `LLM_TIMEOUT_SECONDS` and `LLM_MAX_RETRIES`. Every response
is validated against the Pydantic contract in `backend/schemas.py` before an
agent can contribute it to shared workflow state.

## Testing

```bash
cd creatorflow-ai
backend/venv/bin/pip install -r backend/requirements-dev.txt
LLM_PROVIDER=dummy backend/venv/bin/python -m pytest backend/tests -q
npm run build --prefix frontend
```

GitHub Actions runs the same backend test and frontend build checks for changes
under `creatorflow-ai/`.

## Future improvements

- Run independent agents in parallel when their dependencies allow it
- Add distributed tracing and token/cost reporting
- Add Ruflo MCP integration for external swarm coordination
- Add persistent Ruflo/AgentDB-style memory for creator preferences
- Ground research-heavy topics in cited sources
- Add a visual production calendar export
- Add collaborative editing and per-section approval

## License

This project is available under the [MIT License](../LICENSE).

## Interview explanation

> "CreatorFlow AI is a multi-agent YouTube content assistant inspired by Ruflo. Instead of using one single AI prompt, the system divides the content generation workflow into specialized agents such as Topic Agent, Title Agent, Script Agent, SEO Agent, Thumbnail Agent, Shorts Agent, and Review Agent. The orchestrator coordinates these agents and combines their outputs into a complete YouTube content package. This makes the system modular, scalable, and easier to improve."
