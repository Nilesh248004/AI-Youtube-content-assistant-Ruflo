import json
from typing import Any, Dict

from llm_client import call_llm


class ThumbnailAgent:
    name = "thumbnail_agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = json.dumps(
            {
                "agent": "thumbnail",
                "instructions": (
                    "Generate exactly five compelling thumbnail phrases. "
                    "Each phrase must contain no more than four words."
                ),
                "input": {
                    "request": state["request"],
                    "topic_analysis": state["topic_analysis"],
                    "titles": state["titles"],
                },
            }
        )
        return json.loads(call_llm(prompt))
