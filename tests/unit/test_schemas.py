import pytest
from datetime import datetime, timedelta, timezone
from src.links.schemas import LinkCreate

def test_original_url_auto_scheme(future_expire):
    data = LinkCreate(original_url="https://example.com", expire_at=future_expire)
    assert str(data.original_url).startswith("https://")

def test_expire_at_rounding():
    future_date = datetime.now(timezone.utc) + timedelta(days=1, seconds=42)
    data = LinkCreate(original_url="https://example.com", expire_at=future_date)
    assert data.expire_at.second == 0

def test_expire_at_past_error():
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    with pytest.raises(ValueError):
        LinkCreate(original_url="https://example.com", expire_at=past_date)