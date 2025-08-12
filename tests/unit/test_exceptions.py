from src.links.exceptions import (
    NotUniqueAliasError,
    AliasLengthError,
    LinkExpiredError,
    PermissionDeniedError,
    InvalidURLFormatError
)

def test_not_unique_alias_error():
    err = NotUniqueAliasError("test")
    assert err.status_code == 400
    assert "already exists" in err.detail

def test_alias_length_error():
    err = AliasLengthError("abc")
    assert err.status_code == 400
    assert "must be between" in err.detail

def test_link_expired_error():
    err = LinkExpiredError("code123")
    assert err.status_code == 410
    assert "has expired" in err.detail

def test_permission_denied_error():
    err = PermissionDeniedError("delete link")
    assert err.status_code == 403
    assert "permission" in err.detail

def test_invalid_url_format_error():
    err = InvalidURLFormatError("invalid_url")
    assert err.status_code == 400
    assert "Invalid URL format" in err.detail