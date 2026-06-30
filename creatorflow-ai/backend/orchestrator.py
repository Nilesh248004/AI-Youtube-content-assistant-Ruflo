from typing import Any, Dict

from agents import (
    FinalResponseAgent,
    ReviewAgent,
    ScriptAgent,
    SeoAgent,
    ShortsAgent,
    ThumbnailAgent,
    TitleAgent,
    TopicAgent,
)


class CreatorFlowOrchestrator:
    """Coordinates specialist agents in a Ruflo-style shared-state workflow.

    Ruflo calls this role the harness/coordinator: each specialist receives the
    accumulated workflow state, contributes its bounded result, and hands the
    enriched state to the next agent. The in-memory state is the MVP equivalent
    of Ruflo's shared swarm memory/ledger.
    """

    def __init__(self) -> None:
        self.pipeline = [
            TopicAgent(),
            TitleAgent(),
            ScriptAgent(),
            ThumbnailAgent(),
            SeoAgent(),
            ShortsAgent(),
            ReviewAgent(),
        ]
        self.final_response_agent = FinalResponseAgent()

    def generate(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        state: Dict[str, Any] = {
            "request": request_data,
            "execution_trace": [],
        }

        for agent in self.pipeline:
            contribution = agent.run(state)
            if not isinstance(contribution, dict):
                raise ValueError(f"{agent.name} returned an invalid response.")
            state.update(contribution)
            state["execution_trace"].append(agent.name)

        return self.final_response_agent.run(state)
