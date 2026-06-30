import json
from typing import Any, Dict

from llm_client import call_llm


class SeoAgent:
    name = "seo_agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = json.dumps(
            {
                "agent": "seo",
                "instructions": (
                    "Create a YouTube description, ten SEO tags, eight hashtags, "
                    "and a conversation-starting pinned comment."
                ),
                "input": {
                    "request": state["request"],
                    "topic_analysis": state["topic_analysis"],
                    "titles": state["titles"],
                    "script": state["script"],
                },
            }
        )
        return {"seo": json.loads(call_llm(prompt))}
