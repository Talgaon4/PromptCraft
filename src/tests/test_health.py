def test_health_endpoint(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200

    body = r.json()
    # top-level keys
    assert body["success"] is True
    assert body["errors"] == []

    # nested payload
    payload = body["data"]
    assert payload["status"] == "healthy"
    assert payload["version"] == "1.0.0"
