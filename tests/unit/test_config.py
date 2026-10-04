"""Unit tests for configuration and settings management."""

from core.config.settings import Settings, get_settings


def test_default_settings() -> None:
    """Verify default configuration attributes."""
    settings = Settings()
    assert settings.app_name == "Morrow"
    assert settings.app_version == "0.1.0"
    assert settings.app_env in {"development", "testing", "production"}
    assert settings.api_port == 8000
    assert "postgresql+asyncpg" in settings.database_url


def test_custom_settings_override() -> None:
    """Verify that settings can be customized."""
    settings = Settings(
        app_name="CustomMorrow",
        app_env="production",
        app_version="1.0.0",
        api_port=9000,
    )
    assert settings.app_name == "CustomMorrow"
    assert settings.app_env == "production"
    assert settings.app_version == "1.0.0"
    assert settings.api_port == 9000


def test_get_settings_caching() -> None:
    """Verify that get_settings() returns a cached singleton."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
