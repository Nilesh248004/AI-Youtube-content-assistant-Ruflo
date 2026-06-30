from typing import Any, Dict


class FinalResponseAgent:
    """Deterministically assembles the specialist outputs into the API contract."""

    name = "final_response_agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "request": state["request"],
            "topic_analysis": state["topic_analysis"],
            "titles": state["titles"],
            "script": state["script"],
            "thumbnail_texts": state["thumbnail_texts"],
            "seo": state["seo"],
            "shorts": state["shorts"],
            "review": state["review"],
            "workflow": {
                "style": "Ruflo-inspired sequential multi-agent orchestration",
                "agents_executed": state["execution_trace"] + [self.name],
                "last_run_agents": state.get(
                    "last_run_agents",
                    state["execution_trace"],
                )
                + [self.name],
            },
        }
