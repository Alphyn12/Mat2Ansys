import pytest

from security import validate_and_normalize_matweb_url


def test_validate_and_normalize_accepts_matweb_url(monkeypatch):
    monkeypatch.setattr("security._validate_host_resolution", lambda _host: None)
    out = validate_and_normalize_matweb_url("https://www.matweb.com/search/QuickText.aspx#x")
    assert out == "https://www.matweb.com/search/QuickText.aspx"


@pytest.mark.parametrize(
    "bad_url",
    [
        "http://www.matweb.com/search/QuickText.aspx",
        "https://localhost/admin",
        "https://127.0.0.1/",
        "file:///etc/passwd",
        "https://www.matweb.com:8443/search/QuickText.aspx",
    ],
)
def test_validate_and_normalize_rejects_bad_urls(monkeypatch, bad_url):
    monkeypatch.setattr("security._validate_host_resolution", lambda _host: None)
    with pytest.raises(ValueError):
        validate_and_normalize_matweb_url(bad_url)
