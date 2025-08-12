import pytest


@pytest.mark.asyncio
async def test_create_link_anonymous(client):
    resp = await client.post("/links/shorten", json={"original_url": "https://example.com"})
    assert resp.status_code == 200
    assert "short_id" in resp.json()


@pytest.mark.asyncio
async def test_redirect_link(client):
    create_resp = await client.post("/links/shorten", json={"original_url": "https://example.com"})
    short_id = create_resp.json()["short_id"]

    resp = await client.get(f"/{short_id}", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"] == "https://example.com"


@pytest.mark.asyncio
async def test_redirect_not_found(client):
    resp = await client.get("/nonexistent", follow_redirects=False)
    assert resp.status_code == 404