"""Replaceable LLM boundary for CreatorFlow AI.

Supported providers:
- LLM_PROVIDER=dummy  -> deterministic demo content
- LLM_PROVIDER=openai -> OpenAI API
- LLM_PROVIDER=ollama -> local Ollama model

To switch provider, update backend/.env.
"""

import json
import logging
import os
import re
import time
from typing import Any, Dict, Tuple

from dotenv import load_dotenv
from pydantic import ValidationError

from schemas import agent_json_schema, validate_agent_response

load_dotenv()
logger = logging.getLogger("creatorflow.llm")


def _slug_words(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", value)
    return "".join(word.capitalize() for word in words[:4]) or "YouTubeTips"


def _minutes(duration: str) -> int:
    match = re.search(r"\d+", duration)
    return int(match.group()) if match else 8


def _timeout_seconds() -> float:
    try:
        return max(1.0, float(os.getenv("LLM_TIMEOUT_SECONDS", "60")))
    except ValueError:
        return 60.0


def _max_retries() -> int:
    try:
        return max(0, min(5, int(os.getenv("LLM_MAX_RETRIES", "2"))))
    except ValueError:
        return 2


def _openai_compatible_schema(value: Any) -> Any:
    """Keep strict shape keywords while leaving value constraints to Pydantic."""

    unsupported = {
        "maxItems",
        "maxLength",
        "maximum",
        "minItems",
        "minLength",
        "minimum",
    }
    if isinstance(value, dict):
        return {
            key: _openai_compatible_schema(nested)
            for key, nested in value.items()
            if key not in unsupported
        }
    if isinstance(value, list):
        return [_openai_compatible_schema(item) for item in value]
    return value


# -------------------------
# Dummy LLM responses
# -------------------------

def _topic_response(data: Dict[str, Any]) -> Dict[str, Any]:
    topic = data["topic"]
    audience = data["audience"]
    tone = data["tone"]
    goal = data["goal"]

    return {
        "summary": (
            f"This video explains {topic} for {audience} in a {tone} way, "
            f"with the primary goal of creating a {goal} experience."
        ),
        "recommended_angle": (
            f"Start with the problem viewers are trying to solve, explain the core "
            f"ideas behind {topic}, then use one practical scenario to show when each "
            "concept matters."
        ),
        "audience_needs": [
            "Clear definitions before technical detail",
            "A practical comparison with familiar examples",
            "A simple decision framework viewers can remember",
        ],
        "key_points": [
            f"What {topic} means in plain language",
            "The most important similarities and differences",
            "A real-life use case",
            "Common beginner mistakes",
            "A practical next step",
        ],
    }


def _title_response(data: Dict[str, Any]) -> Dict[str, Any]:
    topic = data["request"]["topic"]
    audience = data["request"]["audience"].title()

    return {
        "titles": [
            f"{topic} Explained Simply",
            f"{topic}: A Beginner's Guide",
            f"Understanding {topic} in 8 Minutes",
            f"{topic} — What You Actually Need to Know",
            f"A Practical Guide to {topic} for {audience}",
        ]
    }


def _script_response(data: Dict[str, Any]) -> Dict[str, Any]:
    request = data["request"]
    topic = request["topic"]
    audience = request["audience"]
    duration = request["duration"]
    goal = request["goal"]
    target_words = _minutes(duration) * 130

    return {
        "estimated_duration": duration,
        "target_word_count": target_words,
        "hook": f"Have you ever wondered what {topic} actually means and why it matters?",
        "introduction": (
            f"Welcome! This video is designed for {audience}. "
            f"We will explain {topic} in a simple way. The goal is {goal}."
        ),
        "main_explanation": [
            {
                "heading": "1. Begin with the problem",
                "content": f"Before learning {topic}, understand the problem it solves.",
            },
            {
                "heading": "2. Understand the core ideas",
                "content": f"Break {topic} into small concepts instead of learning everything at once.",
            },
            {
                "heading": "3. Compare with practical questions",
                "content": (
                    "Ask what problem you are solving, how often it changes, "
                    "and what happens if it fails."
                ),
            },
            {
                "heading": "4. Start small",
                "content": (
                    f"For most beginners, the best way to learn {topic} is to build "
                    "one small practical example first."
                ),
            },
        ],
        "real_life_example": (
            f"Imagine using {topic} in a real project where clarity, decision-making, "
            "and practical understanding matter."
        ),
        "summary": (
            f"To understand {topic}, start with the problem, learn the basics, "
            "and apply it practically."
        ),
        "call_to_action": f"If this made {topic} clearer, like and subscribe.",
    }


def _thumbnail_response(data: Dict[str, Any]) -> Dict[str, Any]:
    topic = data["request"]["topic"]
    words = topic.split()

    if len(words) <= 2:
        topic_text = f"{' '.join(words)} Made Simple"
    elif any(word.lower() == "vs" for word in words):
        topic_text = f"{words[0]} vs {words[-1]}"
    else:
        topic_text = f"{words[0]} {words[1]} Explained"

    return {
        "thumbnail_texts": [
            topic_text,
            "Which One Wins?",
            "Stop Being Confused",
            "Choose The Right Tool",
            "Beginner Guide Inside",
        ]
    }


def _seo_response(data: Dict[str, Any]) -> Dict[str, Any]:
    request = data["request"]
    topic = request["topic"]
    audience = request["audience"]
    topic_hashtag = _slug_words(topic)

    return {
        "description": (
            f"Learn {topic} in a clear, practical way. "
            f"This guide is made for {audience} and explains the key ideas, "
            "real-life examples, and beginner-friendly takeaways."
        ),
        "tags": [
            topic,
            f"{topic} tutorial",
            f"{topic} for beginners",
            f"learn {topic}",
            f"{topic} explained",
            "technology explained",
            "beginner tutorial",
            "educational video",
            "creator tips",
            "youtube content",
        ],
        "hashtags": [
            f"#{topic_hashtag}",
            "#TechExplained",
            "#BeginnerTutorial",
            "#LearnTech",
            "#YouTubeLearning",
            "#CreatorFlowAI",
            "#ContentCreation",
            "#Education",
        ],
        "pinned_comment": f"What is your biggest question about {topic}?",
    }


def _shorts_response(data: Dict[str, Any]) -> Dict[str, Any]:
    topic = data["request"]["topic"]
    topic_hashtag = _slug_words(topic)

    return {
        "thirty_second_script": (
            f"Still confused by {topic}? Start with the problem first. "
            "Do not learn buzzwords blindly. Ask what it solves, where it is used, "
            "and when you actually need it. Follow for more simple explanations."
        ),
        "sixty_second_script": (
            f"Here is {topic} in one minute. First, understand the problem. "
            "Second, learn the basic concept. Third, apply it in a small project. "
            "Do not jump directly into advanced details. The best way to learn is "
            "to connect the concept with a real use case."
        ),
        "instagram_reel_caption": (
            f"{topic} does not need to feel complicated. Save this simple explanation."
        ),
        "hashtags": [
            f"#{topic_hashtag}",
            "#TechShorts",
            "#LearnIn60Seconds",
            "#BeginnerTech",
            "#CreatorTips",
        ],
    }


def _review_response(data: Dict[str, Any]) -> Dict[str, Any]:
    topic = data["request"]["topic"]

    return {
        "quality_score": 8.7,
        "strengths": [
            "The content matches the requested audience and tone.",
            "The structure is beginner-friendly.",
            "SEO and short-form assets are consistent.",
        ],
        "improvements": [
            f"Add one topic-specific statistic or real example for {topic}.",
            "Improve pacing after reading the script aloud.",
            "Add the creator's personal experience before publishing.",
        ],
        "final_recommendation": "Ready for demo. Add real examples before publishing.",
    }


_DUMMY_HANDLERS = {
    "topic": _topic_response,
    "title": _title_response,
    "script": _script_response,
    "thumbnail": _thumbnail_response,
    "seo": _seo_response,
    "shorts": _shorts_response,
    "review": _review_response,
}


# -------------------------
# JSON schema per agent
# -------------------------

def _schema_for_agent(agent_name: str) -> Dict[str, Any]:
    return agent_json_schema(agent_name)


def _agent_rules(agent_name: str) -> str:
    rules = {
        "topic": """
- Analyze the topic clearly.
- Keep the meaning consistent across the full workflow.
- audience_needs must contain at least 3 items.
- key_points must contain at least 5 items.
""",
        "title": """
- Return exactly 5 titles.
- Titles should be catchy but not misleading.
- Titles should be suitable for YouTube.
""",
        "script": """
- Create a proper long-form YouTube script.
- target_word_count must match the video duration.
- For 8 minutes, target_word_count should be around 1040.
- main_explanation must contain at least 4 sections.
""",
        "thumbnail": """
- Return exactly 5 thumbnail text ideas.
- Each thumbnail text must be maximum 4 words.
- Make them short, bold, and clear.
""",
        "seo": """
- Return exactly 10 tags.
- Return exactly 8 hashtags.
- pinned_comment must not be empty.
- Description should be SEO-friendly and useful.
""",
        "shorts": """
- Return a 30-second script.
- Return a 60-second script.
- Return one Instagram Reel caption.
- Return exactly 5 hashtags.
""",
        "review": """
- quality_score must be a number from 1 to 10.
- Give at least 3 strengths.
- Give at least 3 improvements.
- Give a clear final recommendation.
""",
    }

    return rules.get(agent_name, "")


def _build_system_prompt(agent_name: str, payload: Dict[str, Any]) -> str:
    return f"""
You are the {agent_name} agent inside CreatorFlow AI.

CreatorFlow AI is a multi-agent YouTube content assistant.

Your job:
Return ONLY valid JSON.
Do not return markdown.
Do not add explanation outside JSON.

General rules:
- Match the expected JSON keys exactly.
- Do not add extra keys.
- Generate content based on the user's topic, audience, language, tone, duration, and goal.
- Keep the output useful for YouTube creators.
- Do not wrap the JSON in markdown blocks.

Agent-specific rules:
{_agent_rules(agent_name)}

Expected JSON schema:
{json.dumps(_schema_for_agent(agent_name), indent=2)}

Input data:
{json.dumps(payload, indent=2)}
"""


def _extract_envelope(prompt: str) -> Tuple[str, Dict[str, Any]]:
    try:
        envelope = json.loads(prompt)
        agent_name = envelope["agent"]
        payload = envelope["input"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError("The LLM prompt did not match the agent contract.") from exc

    return agent_name, payload


# -------------------------
# OpenAI provider
# -------------------------

def _call_openai(prompt: str) -> str:
    try:
        from openai import OpenAI
        from openai import AuthenticationError, APIError, RateLimitError
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI package is not installed. Run: pip install openai"
        ) from exc

    agent_name, payload = _extract_envelope(prompt)

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing in .env")

    client = OpenAI(
        api_key=api_key,
        timeout=_timeout_seconds(),
        max_retries=_max_retries(),
    )
    system_prompt = _build_system_prompt(agent_name, payload)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": "Generate the required JSON output for this agent.",
                },
            ],
            temperature=0.7,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": f"{agent_name}_output",
                    "strict": True,
                    "schema": _openai_compatible_schema(
                        _schema_for_agent(agent_name)
                    ),
                },
            },
        )

    except RateLimitError as exc:
        raise RuntimeError(
            "OpenAI API quota exceeded. Add OpenAI billing/credits or switch LLM_PROVIDER=ollama or dummy."
        ) from exc

    except AuthenticationError as exc:
        raise RuntimeError(
            "OpenAI authentication failed. Check your OPENAI_API_KEY."
        ) from exc

    except APIError as exc:
        raise RuntimeError(
            "OpenAI API error. Try again later or switch provider."
        ) from exc

    content = response.choices[0].message.content

    if not content:
        raise ValueError("OpenAI returned empty response.")

    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("OpenAI returned invalid JSON.") from exc

    return content


# -------------------------
# Ollama provider
# -------------------------

def _call_ollama(prompt: str) -> str:
    try:
        import ollama
    except ImportError as exc:
        raise RuntimeError(
            "Ollama Python package is not installed. Run: pip install ollama"
        ) from exc

    agent_name, payload = _extract_envelope(prompt)

    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    client = ollama.Client(host=host, timeout=_timeout_seconds())
    system_prompt = _build_system_prompt(agent_name, payload)

    response = None
    for attempt in range(_max_retries() + 1):
        try:
            response = client.generate(
                model=model,
                system=system_prompt,
                prompt="Generate the required JSON output for this agent.",
                stream=False,
                format="json",
                options={
                    "temperature": 0.7,
                },
            )
            break
        except Exception as exc:
            if attempt >= _max_retries():
                raise RuntimeError(
                    "Ollama call failed. Make sure Ollama is running and the configured model is available."
                ) from exc
            logger.warning(
                "Ollama request failed; retrying",
                extra={"attempt": attempt + 1},
            )
            time.sleep(min(2**attempt, 4))

    content = response.get("response", "") if response else ""

    if not content:
        raise ValueError("Ollama returned empty response.")

    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("Ollama returned invalid JSON.") from exc

    return content


# -------------------------
# Dummy provider
# -------------------------

def _call_dummy(prompt: str) -> str:
    agent_name, payload = _extract_envelope(prompt)

    try:
        handler = _DUMMY_HANDLERS[agent_name]
    except KeyError as exc:
        raise ValueError(f"No dummy handler found for agent: {agent_name}") from exc

    return json.dumps(handler(payload), ensure_ascii=False)


# -------------------------
# Public LLM boundary
# -------------------------

def call_llm(prompt: str) -> str:
    provider = os.getenv("LLM_PROVIDER", "dummy").lower()
    agent_name, _ = _extract_envelope(prompt)

    if provider == "openai":
        content = _call_openai(prompt)
    elif provider == "ollama":
        content = _call_ollama(prompt)
    elif provider == "dummy":
        content = _call_dummy(prompt)
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER='{provider}'. Use dummy, openai, or ollama."
        )

    try:
        return validate_agent_response(agent_name, content)
    except (ValidationError, ValueError) as exc:
        raise ValueError(
            f"{agent_name} agent returned content that failed validation."
        ) from exc
