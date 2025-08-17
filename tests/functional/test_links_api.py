import pytest
import uuid

@pytest.mark.asyncio
async def test_create_link_anonymous(client, future_expire):
    resp = await client.post("/links/shorten", json={
        "original_url": "https://anon.example",
        "custom_alias": f"anon-{uuid.uuid4().hex[:6]}",
        "expire_at": future_expire
    })
    assert resp.status_code in (200, 201)
    body = resp.json()
    assert "short_id" in body

@pytest.mark.asyncio
async def test_create_link_with_auth(client, registered_user, future_expire):
    resp = await client.post("/links/shorten", json={
        "original_url": "https://auth.example",
        "custom_alias": f"auth-{uuid.uuid4().hex[:6]}",
        "expire_at": future_expire
    })
    assert resp.status_code in (200, 201)
    body = resp.json()
    assert "short_id" in body

@pytest.mark.asyncio
async def test_redirect_link(client, registered_user, future_expire):
    target = "https://redirect.example"
    create = await client.post("/links/shorten", json={
        "original_url": target,
        "custom_alias": f"redir-{uuid.uuid4().hex[:6]}",
        "expire_at": future_expire
    })
    short_id = create.json()["short_id"]

    resp1 = await client.get(f"/links/{short_id}", follow_redirects=False)
    if resp1.status_code in (302, 307):
        location = resp1.headers.get("location")
        assert location.rstrip("/") == target.rstrip("/")
    else:
        resp2 = await client.get(f"/r/{short_id}", follow_redirects=False)
        assert resp2.status_code in (302, 307)
        location = resp2.headers.get("location")
        assert location.rstrip("/") == target.rstrip("/")

@pytest.mark.asyncio
async def test_redirect_not_found(client):
    resp = await client.get("/r/notfound123", follow_redirects=False)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_stats_access_control(client, registered_user, future_expire):
    create = await client.post("/links/shorten", json={
        "original_url": "https://mine.example",
        "custom_alias": f"mine-{uuid.uuid4().hex[:6]}",
        "expire_at": future_expire
    })
    short_id = create.json()["short_id"]
    other_email = f"other-{uuid.uuid4().hex[:8]}@example.com"
    await client.post("/auth/register", json={
        "id": 2,
        "email": other_email,
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    login = await client.post("/auth/jwt/login", data={
        "username": other_email,
        "password": "string",
        "grant_type": "password"
    })
    cookie = login.headers.get("set-cookie")
    if cookie:
        client.headers.update({"cookie": cookie})
    resp = await client.get(f"/links/{short_id}/stats")
    assert resp.status_code in (403, 404)

@pytest.mark.asyncio
async def test_update_and_delete_link(client, registered_user, future_expire):
    create = await client.post("/links/shorten", json={
        "original_url": "https://update.example",
        "custom_alias": f"upd-{uuid.uuid4().hex[:6]}",
        "expire_at": future_expire
    })
    short_id = create.json()["short_id"]
    update = await client.put(f"/links/{short_id}", json={
        "original_url": "https://updated.example",
        "expire_at": future_expire
    })
    assert update.status_code in (200, 204)
    delete = await client.delete(f"/links/{short_id}")
    assert delete.status_code in (200, 204)

@pytest.mark.asyncio
async def test_search_links(client, registered_user, future_expire):
    term = f"https://search-{uuid.uuid4().hex[:6]}.example"
    for i in range(2):
        resp = await client.post("/links/shorten", json={
            "original_url": f"{term}/p{i}",
            "custom_alias": f"s{i}-{uuid.uuid4().hex[:6]}",
            "expire_at": future_expire
        })
        assert resp.status_code in (200, 201)
    found = await client.get("/links/search/", params={"original_url": term})
    assert found.status_code == 200
    results = found.json()
    assert len(results) >= 2