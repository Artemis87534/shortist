from datetime import datetime, timedelta
from src.links.models import Link


def test_link_expiration():
    expired_link = Link(expire_at=datetime.now() - timedelta(days=1))
    active_link = Link(expire_at=datetime.now() + timedelta(days=1))

    assert expired_link.is_expired is True
    assert active_link.is_expired is False