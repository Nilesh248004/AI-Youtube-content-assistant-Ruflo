import json
from typing import Any, Dict

from llm_client import call_llm


class TitleAgent:
    name = "title_agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = json.dumps(
            {
                "agent": "title",
                "instructions": "Generate exactly five catchy, accurate, non-clickbait titles.",
                "input": {
                    "request": state["request"],
                    "topic_analysis": state["topic_analysis"],
                },
            }
        )
        return json.loads(call_llm(prompt))
