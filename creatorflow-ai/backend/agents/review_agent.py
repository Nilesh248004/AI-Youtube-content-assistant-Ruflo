import json
from typing import Any, Dict

from llm_client import call_llm


class ReviewAgent:
    name = "review_agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        package_to_review = {
            key: value
            for key, value in state.items()
            if key not in {"execution_trace", "review"}
        }
        prompt = json.dumps(
            {
                "agent": "review",
                "instructions": (
                    "Review the entire package for clarity, consistency, usefulness, "
                    "audience fit, and publishing readiness. Score it out of ten."
                ),
                "input": {
                    "request": state["request"],
                    "content_package": package_to_review,
                },
            }
        )
        return {"review": json.loads(call_llm(prompt))}
