import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from src.links import crud, models
from src.links.exceptions import NotUniqueAliasError

@pytest.mark.asyncio
async def test_generate_short_id_length():
    short_id = crud.generate_short_id(8)
    assert len(short_id) == 8
    assert all(c.isalnum() for c in short_id)

@pytest.mark.asyncio
async def test_generate_short_id_uniqueness():
    ids = {crud.generate_short_id() for _ in range(500)}
    assert len(ids) == 500

@pytest.mark.asyncio
async def test_increment_click_count(db_session: AsyncSession):
    link = models.Link(
        original_url="https://example.com",
        short_id="abc123",
        created_at=datetime.now(timezone.utc),
        expire_at=None,
        click_count=0
    )
    db_session.add(link)
    await db_session.commit()
    await db_session.refresh(link)
    await crud.increment_click_count(db_session, link)
    result = await db_session.get(models.Link, link.id)
    assert result.click_count == 1

@pytest.mark.asyncio
async def test_create_link_duplicate_alias(db_session: AsyncSession):
    link = models.Link(
        original_url="https://example.com",
        short_id="alias",
        custom_alias="alias",
        created_at=datetime.now(timezone.utc),
        expire_at=None,
        click_count=0
    )
    db_session.add(link)
    await db_session.commit()
    with pytest.raises(NotUniqueAliasError):
        await crud.create_link(
            db=db_session,
            original_url="https://test.com",
            custom_alias="alias"
        )

@pytest.mark.asyncio
async def test_create_update_delete_link(db_session: AsyncSession):
    link = await crud.create_link(db_session, original_url="https://google.com")
    assert link.id is not None
    updated = await crud.update_link(db_session, link, "https://yahoo.com")
    assert updated.original_url == "https://yahoo.com"
    await crud.delete_link(db_session, link)
    found = await crud.get_link_by_short_id(db_session, link.short_id)
    assert found is None