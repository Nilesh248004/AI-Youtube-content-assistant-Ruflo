# CreatorFlow AI

CreatorFlow AI is a runnable React + FastAPI MVP that turns one YouTube topic
into a complete content package. It uses a lightweight, Ruflo-inspired
multi-agent workflow with specialist agents for strategy, titles, scripting,
thumbnails, SEO, short-form content, review, and final response assembly.

No database or API key is required. The included dummy LLM provider produces
realistic, deterministic demo output and is isolated behind one replaceable
function.

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
- Provider-ready LLM boundary with no API key needed for the demo

## Folder structure

```text
creatorflow-ai/
├── backend/
│   ├── main.py
│   ├── orchestrator.py
│   ├── llm_client.py
│   ├── requirements.txt
│   ├── README_BACKEND.md
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
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api.js
│       └── App.css
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
backend URL, start Vite with a `VITE_API_URL` environment variable.

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
    "agents_executed": ["topic_agent", "...", "final_response_agent"]
  }
}
```

## Connecting a real LLM

Every specialist sends a JSON prompt envelope to:

```python
def call_llm(prompt: str) -> str:
    ...
```

Replace the body of `backend/llm_client.py::call_llm` with an OpenAI, Gemini,
Groq, or local Ollama request. Keep the function signature and return a valid
JSON string matching the specialist's current contract. This central boundary
keeps provider credentials and SDK details out of the agents and orchestrator.

## Future improvements

- Add selectable OpenAI, Gemini, Groq, and Ollama providers
- Validate each LLM result with dedicated Pydantic response models
- Run independent agents in parallel when their dependencies allow it
- Add retries, timeouts, tracing, and token/cost reporting
- Add Ruflo MCP integration for external swarm coordination
- Add persistent Ruflo/AgentDB-style memory for creator preferences
- Ground research-heavy topics in cited sources
- Export the package to Markdown, JSON, or a production calendar
- Add script editing, regeneration, and per-section approval

## Interview explanation

> "CreatorFlow AI is a multi-agent YouTube content assistant inspired by Ruflo. Instead of using one single AI prompt, the system divides the content generation workflow into specialized agents such as Topic Agent, Title Agent, Script Agent, SEO Agent, Thumbnail Agent, Shorts Agent, and Review Agent. The orchestrator coordinates these agents and combines their outputs into a complete YouTube content package. This makes the system modular, scalable, and easier to improve."
