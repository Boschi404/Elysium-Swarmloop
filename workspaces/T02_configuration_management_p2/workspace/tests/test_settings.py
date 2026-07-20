"""
Pydantic settings tests — fast-app entry point.
"""

from app.settings import get_settings


class TestSettings:
    """Validates settings loading from environment /.env."""

    def test_get_settings_returns_singleton(self):
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_app_name_is_string(self):
        s = get_settings()
        assert isinstance(s.app_name, str)
        assert len(s.app_name) > 0

    def test_database_url_has_asyncpg(self):
        s = get_settings()
        assert "asyncpg" in s.database_url

    def test_redis_url_has_password_placeholder(self):
        s = get_settings()
        assert "redis://" in s.redis_url
