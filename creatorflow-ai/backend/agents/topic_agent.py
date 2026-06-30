import json
from typing import Any, Dict

from llm_client import call_llm


class TopicAgent:
    name = "topic_agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = json.dumps(
            {
                "agent": "topic",
                "instructions": (
                    "Analyze the topic, audience, language, tone, duration, and goal. "
                    "Return a concise content strategy as JSON."
                ),
                "input": state["request"],
            }
        )
        return {"topic_analysis": json.loads(call_llm(prompt))}
