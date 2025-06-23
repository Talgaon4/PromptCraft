import uuid

def _create_prompt(client):
    body = {"text": f"T {uuid.uuid4()}", "description": "demo"}
    return client.post("/api/v1/prompts", json=body).json()["data"]["id"]

def test_instance_and_response_flow(client):
    # 1. create prompt
    prompt_id = _create_prompt(client)

    # 2. create instance
    inst_body = {"formatted_text": "Translate: 你好"}
    r = client.post(f"/api/v1/prompts/{prompt_id}/instances", json=inst_body)
    assert r.status_code == 201
    instance_id = r.json()["data"]["id"]

    # 3. list instances
    r = client.get(f"/api/v1/prompts/{prompt_id}/instances")
    assert any(i["id"] == instance_id for i in r.json()["data"]["items"])

    # 4. create response
    resp_body = {"content": "Hello", "metadata": {"model": "gpt"}}
    r = client.post(f"/api/v1/instances/{instance_id}/responses", json=resp_body)
    assert r.status_code == 201
    response_id = r.json()["data"]["id"]

    # 5. list responses
    r = client.get(f"/api/v1/instances/{instance_id}/responses")
    assert any(rp["id"] == response_id for rp in r.json()["data"]["items"])
