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
        self.section_indexes = {
            "topic_analysis": 0,
            "titles": 1,
            "script": 2,
            "thumbnail_texts": 3,
            "seo": 4,
            "shorts": 5,
            "review": 6,
        }

    def generate(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        state: Dict[str, Any] = {
            "request": request_data,
            "execution_trace": [],
            "last_run_agents": [],
        }

        for agent in self.pipeline:
            contribution = agent.run(state)
            if not isinstance(contribution, dict):
                raise ValueError(f"{agent.name} returned an invalid response.")
            state.update(contribution)
            state["execution_trace"].append(agent.name)
            state["last_run_agents"].append(agent.name)

        return self.final_response_agent.run(state)

    def regenerate(
        self,
        section: str,
        current_package: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Rerun a section and all downstream agents without changing upstream work."""

        if section not in self.section_indexes:
            raise ValueError(f"Unsupported section: {section}")

        start_index = self.section_indexes[section]
        state = {
            key: value
            for key, value in current_package.items()
            if key != "workflow"
        }
        state["execution_trace"] = [
            agent.name for agent in self.pipeline[:start_index]
        ]
        state["last_run_agents"] = []

        for agent in self.pipeline[start_index:]:
            contribution = agent.run(state)
            if not isinstance(contribution, dict):
                raise ValueError(f"{agent.name} returned an invalid response.")
            state.update(contribution)
            state["execution_trace"].append(agent.name)
            state["last_run_agents"].append(agent.name)

        return self.final_response_agent.run(state)
