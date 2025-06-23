import uuid

def _create(client):
    body = {
        "text": f"Test {uuid.uuid4()}",
        "description": "init",
    }
    return client.post("/api/v1/prompts", json=body).json()["data"]["id"]

def test_get_and_update(client):
    pid = _create(client)

    # GET one
    r = client.get(f"/api/v1/prompts/{pid}")
    assert r.status_code == 200
    assert r.json()["data"]["id"] == pid

    # LIST
    r = client.get("/api/v1/prompts?offset=0&limit=5")
    assert r.status_code == 200
    assert any(item["id"] == pid for item in r.json()["data"]["items"])

    # UPDATE
    upd = {"description": "updated desc"}
    r = client.put(f"/api/v1/prompts/{pid}", json=upd)
    assert r.status_code == 200
    assert r.json()["data"]["description"] == "updated desc"
