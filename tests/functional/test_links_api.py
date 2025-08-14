import uuid
import pytest
from datetime import datetime, timedelta, timezone

@pytest.mark.asyncio
async def test_create_link_anonymous(client, future_expire):
    body = {
        "original_url": "https://example.com",
        "custom_alias": f"anon-{uuid.uuid4().hex[:6]}",
        "expire_at": future_expire
    }
    resp = await client.post("/links/shorten", json=body)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "short_id" in data
    assert data["original_url"] == body["original_url"]

@pytest.mark.asyncio
async def test_create_link_with_auth(client, registered_user, future_expire):
    body = {
        "original_url": "https://auth-example.com",
        "custom_alias": f"auth-{uuid.uuid4().hex[:6]}",
        "expire_at": future_expire
    }
    resp = await client.post("/links/shorten", json=body)
    assert resp.status_code in (200, 201)
    assert "short_id" in resp.json()

@pytest.mark.asyncio
async def test_redirect_link(client, future_expire):
    create = await client.post("/links/shorten", json={
        "original_url": "https://example.org/page",
        "custom_alias": f"redir-{uuid.uuid4().hex[:6]}",
        "expire_at": future_expire
    })
    assert create.status_code in (200, 201)
    short_id = create.json()["short_id"]

    resp = await client.get(f"/links/{short_id}", follow_redirects=False)
    assert resp.status_code in (302, 307)

@pytest.mark.asyncio
async def test_redirect_not_found(client):
    resp = await client.get("/links/not-existing", follow_redirects=False)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_stats_access_control(client, registered_user, future_expire):
    create = await client.post("/links/shorten", json={
        "original_url": "https://mine.example",
        "custom_alias": f"mine-{uuid.uuid4().hex[:6]}",
        "expire_at": future_expire
    })
    assert create.status_code in (200, 201)
    short_id = create.json()["short_id"]

    other_email = f"other-{uuid.uuid4().hex[:8]}@example.com"
    reg2 = await client.post("/auth/register", json={
        "id": 2,
        "email": other_email,
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    })
    assert reg2.status_code in (200, 201)
    login2 = await client.post("/auth/jwt/login", data={
        "username": other_email,
        "password": "string",
        "grant_type": "password"
    })
    assert login2.status_code in (200, 204)

    resp_forbidden = await client.get(f"/links/{short_id}/stats")
    assert resp_forbidden.status_code in (403, 404)

@pytest.mark.asyncio
async def test_update_and_delete_link(client, registered_user, future_expire):
    create = await client.post("/links/shorten", json={
        "original_url": "https://update.example",
        "custom_alias": f"upd-{uuid.uuid4().hex[:6]}",
        "expire_at": future_expire
    })
    assert create.status_code in (200, 201)
    short_id = create.json()["short_id"]

    update = await client.put(f"/links/{short_id}", json={
        "original_url": "https://updated.example",
        "expire_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
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
    items = found.json()
    assert isinstance(items, list)
    assert len(items) >= 2