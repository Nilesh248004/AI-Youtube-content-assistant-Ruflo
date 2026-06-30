import asyncio

import httpx

import main


def request(method: str, path: str, **kwargs) -> httpx.Response:
    async def send() -> httpx.Response:
        transport = httpx.ASGITransport(
            app=main.app,
            raise_app_exceptions=False,
        )
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(send())


def test_service_information_is_safe() -> None:
    response = request("GET", "/")

    assert response.status_code == 200
    assert response.json()["provider"] == "dummy"
    assert "OPENAI_API_KEY" not in response.text


def test_generate_returns_complete_content_package() -> None:
    response = request(
        "POST",
        "/generate",
        json={"topic": "Docker vs Kubernetes"},
    )

    assert response.status_code == 200
    content = response.json()
    assert len(content["titles"]) == 5
    assert len(content["thumbnail_texts"]) == 5
    assert len(content["seo"]["tags"]) == 10
    assert len(content["seo"]["hashtags"]) == 8
    assert content["workflow"]["agents_executed"][-1] == "final_response_agent"


def test_generate_rejects_blank_topic() -> None:
    response = request("POST", "/generate", json={"topic": "   "})

    assert response.status_code == 422


def test_regenerate_preserves_upstream_sections() -> None:
    initial = request(
        "POST",
        "/generate",
        json={"topic": "Docker vs Kubernetes"},
    ).json()
    initial["titles"][0] = "A deliberately preserved title"

    response = request(
        "POST",
        "/regenerate/script",
        json={"current_package": initial},
    )

    assert response.status_code == 200
    regenerated = response.json()
    assert regenerated["titles"][0] == "A deliberately preserved title"
    assert regenerated["workflow"]["last_run_agents"][0] == "script_agent"
    assert regenerated["workflow"]["last_run_agents"][-1] == "final_response_agent"


def test_internal_errors_are_not_exposed(monkeypatch) -> None:
    def fail_generation(_request_data):
        raise RuntimeError("private provider detail")

    monkeypatch.setattr(main.orchestrator, "generate", fail_generation)
    response = request("POST", "/generate", json={"topic": "Safe error test"})

    assert response.status_code == 503
    assert "private provider detail" not in response.text
    assert "provider is unavailable" in response.json()["detail"]
