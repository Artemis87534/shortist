import pytest

@pytest.mark.asyncio
async def test_create_link_anonymous(client, future_expire):
    resp = await client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "expire_at": future_expire
    })
    assert resp.status_code == 200
    assert "short_id" in resp.json()

@pytest.mark.asyncio
async def test_create_link_with_auth(client, registered_user, future_expire):
    resp = await client.post("/links/shorten", json={
        "original_url": "https://auth.com",
        "expire_at": future_expire
    }, headers=registered_user)
    assert resp.status_code == 200
    assert resp.json()["original_url"] == "https://auth.com"

@pytest.mark.asyncio
async def test_redirect_link(client, future_expire):
    create_resp = await client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "expire_at": future_expire
    })
    short_id = create_resp.json()["short_id"]
    resp = await client.get(f"/links/{short_id}", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"].rstrip("/") == "https://example.com"

@pytest.mark.asyncio
async def test_redirect_not_found(client):
    resp = await client.get("/links/nonexistent", follow_redirects=False)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_stats_access_control(client, registered_user, future_expire):
    create_resp = await client.post("/links/shorten", json={
        "original_url": "https://stats.com",
        "expire_at": future_expire
    }, headers=registered_user)
    short_id = create_resp.json()["short_id"]
    resp = await client.get(f"/links/{short_id}/stats", headers=registered_user)
    assert resp.status_code == 200
    assert resp.json()["short_id"] == short_id
    resp2 = await client.get(f"/links/{short_id}/stats")
    assert resp2.status_code == 404

@pytest.mark.asyncio
async def test_update_and_delete_link(client, registered_user, future_expire):
    create_resp = await client.post("/links/shorten", json={
        "original_url": "https://update.com",
        "expire_at": future_expire
    }, headers=registered_user)
    short_id = create_resp.json()["short_id"]
    update_resp = await client.put(f"/links/{short_id}", json={
        "original_url": "https://updated.com",
        "expire_at": future_expire
    }, headers=registered_user)
    assert update_resp.status_code == 200
    assert update_resp.json()["original_url"] == "https://updated.com"
    delete_resp = await client.delete(f"/links/{short_id}", headers=registered_user)
    assert delete_resp.status_code == 200
    delete_resp2 = await client.delete(f"/links/{short_id}", headers=registered_user)
    assert delete_resp2.status_code == 404

@pytest.mark.asyncio
async def test_search_links(client, registered_user, future_expire):
    await client.post("/links/shorten", json={
        "original_url": "https://search.com",
        "expire_at": future_expire
    }, headers=registered_user)
    resp = await client.get("/links/search/", params={"original_url": "search"}, headers=registered_user)
    assert resp.status_code == 200
    assert any("search.com" in link["original_url"] for link in resp.json())