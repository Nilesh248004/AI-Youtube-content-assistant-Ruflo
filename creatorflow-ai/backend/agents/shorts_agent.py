import json
from typing import Any, Dict

from llm_client import call_llm


class ShortsAgent:
    name = "shorts_agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = json.dumps(
            {
                "agent": "shorts",
                "instructions": (
                    "Repurpose the long-form idea into 30-second and 60-second scripts, "
                    "an Instagram Reel caption, and Shorts hashtags."
                ),
                "input": {
                    "request": state["request"],
                    "topic_analysis": state["topic_analysis"],
                    "script": state["script"],
                },
            }
        )
        return {"shorts": json.loads(call_llm(prompt))}
