import pytest

pytestmark = pytest.mark.asyncio


async def test_create_short_link(client):
    response = await client.post("/links/shorten", json={
        "original_url": "https://example.com"
    })
    assert response.status_code == 200
    data = response.json()
    assert "short_id" in data
    assert data["short_id"]


async def test_redirect_link(client):
    create_resp = await client.post("/links/shorten", json={
        "original_url": "https://example.com"
    })
    short_id = create_resp.json()["short_id"]

    redirect_resp = await client.get(f"/links/{short_id}", allow_redirects=False)
    assert redirect_resp.status_code == 307
    assert "location" in redirect_resp.headers
    assert redirect_resp.headers["location"] == "https://example.com"