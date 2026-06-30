import json
from typing import Any, Dict

from llm_client import call_llm


class ScriptAgent:
    name = "script_agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = json.dumps(
            {
                "agent": "script",
                "instructions": (
                    "Write a complete video script with a hook, introduction, main "
                    "explanation, real-life example, summary, and call to action."
                ),
                "input": {
                    "request": state["request"],
                    "topic_analysis": state["topic_analysis"],
                    "titles": state["titles"],
                },
            }
        )
        return {"script": json.loads(call_llm(prompt))}
