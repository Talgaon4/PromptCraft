import uuid

def test_create_prompt(client):
    body = {
        "text": f"Unit-test prompt {uuid.uuid4()}",
        "description": "created by pytest",
    }
    r = client.post("/api/v1/prompts", json=body)
    assert r.status_code == 201

    outer = r.json()
    assert outer["success"] is True
    data = outer["data"]
    assert data["text"] == body["text"]
    assert data["version"] == 1
