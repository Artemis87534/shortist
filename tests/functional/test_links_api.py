def test_create_short_link(client):
    response = client.post("/links/shorten", json={
        "original_url": "https://example.com"
    })
    assert response.status_code == 200
    assert "short_id" in response.json()

def test_redirect_link(client):
    create_resp = client.post(...)
    short_id = create_resp.json()["short_id"]
    
    redirect_resp = client.get(f"/links/{short_id}", allow_redirects=False)
    assert redirect_resp.status_code == 307