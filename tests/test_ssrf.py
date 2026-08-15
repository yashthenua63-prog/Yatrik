import pytest
from app.collectors.base import is_safe_url, BaseCollector

def test_safe_urls():
    assert is_safe_url("https://www.google.com") == True
    assert is_safe_url("http://example.com") == True

def test_unsafe_urls():
    assert is_safe_url("http://localhost") == False
    assert is_safe_url("http://127.0.0.1") == False
    assert is_safe_url("http://169.254.169.254") == False
    assert is_safe_url("http://10.0.0.1") == False
    assert is_safe_url("http://172.16.0.5") == False
    assert is_safe_url("http://192.168.1.1") == False
    assert is_safe_url("http://[::1]") == False

def test_invalid_scheme():
    assert is_safe_url("file:///etc/passwd") == False
    assert is_safe_url("ftp://example.com") == False

def test_base_collector_ssrf_blocking():
    collector = BaseCollector("http://169.254.169.254/latest/meta-data")
    result = collector.fetch_page()
    assert result is None
