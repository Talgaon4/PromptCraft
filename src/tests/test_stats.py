# src/tests/test_stats.py
import uuid

def _full_flow(client, scores):
    p_id = client.post(
        "/api/v1/prompts",
        json={"text": f"T {uuid.uuid4()}", "description": ""},
    ).json()["data"]["id"]

    _add_feedback(client, p_id, scores)
    return p_id


def _add_feedback(client, prompt_id, scores):

    inst_id = client.post(
        f"/api/v1/prompts/{prompt_id}/instances",
        json={"formatted_text": "Ping"},
    ).json()["data"]["id"]

    resp_id = client.post(
        f"/api/v1/instances/{inst_id}/responses",
        json={"content": "Pong"},
    ).json()["data"]["id"]

    for s in scores:
        client.post(f"/api/v1/responses/{resp_id}/feedback", json={"score": s})


def test_stats_and_readiness(client):
    pid = _full_flow(client, [0.8, 0.6, 0.9])

    stats = client.get(f"/api/v1/prompts/{pid}/stats").json()["data"]
    assert stats["total_feedback"] == 3
    assert round(stats["avg_score"], 2) == 0.77

    rdy = client.get(f"/api/v1/prompts/{pid}/optimization/readiness").json()["data"]
    assert rdy["ready"] is False

    _add_feedback(client, pid, [0.7, 0.7])

    rdy2 = client.get(f"/api/v1/prompts/{pid}/optimization/readiness").json()["data"]
    assert rdy2["ready"] is True
