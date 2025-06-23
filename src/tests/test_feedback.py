import uuid

def _create_full_flow(client, score=0.8):
    # create prompt -> instance -> response
    p_id = client.post("/api/v1/prompts", json={"text": f"T {uuid.uuid4()}", "description": "d"}).json()["data"]["id"]
    inst_id = client.post(f"/api/v1/prompts/{p_id}/instances", json={"formatted_text": "Ping"}).json()["data"]["id"]
    resp_id = client.post(f"/api/v1/instances/{inst_id}/responses", json={"content": "Pong"}).json()["data"]["id"]
    fb = client.post(f"/api/v1/responses/{resp_id}/feedback", json={"score": score}).json()["data"]["id"]
    return p_id, fb

def test_feedback_flow(client):
    prompt_id, fb_id = _create_full_flow(client)

    # list prompt feedback
    r = client.get(f"/api/v1/prompts/{prompt_id}/feedback")
    assert any(fb["id"] == fb_id for fb in r.json()["data"]["items"])

    # stats
    stats = client.get(f"/api/v1/prompts/{prompt_id}/stats").json()["data"]
    assert stats["total_feedback"] == 1
    assert stats["avg_score"] == 0.8

    # readiness (needs 5)
    rd = client.get(f"/api/v1/prompts/{prompt_id}/optimization/readiness").json()["data"]
    assert rd["ready"] is False
