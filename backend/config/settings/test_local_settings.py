import importlib
import sys


def reload_local_settings(monkeypatch, **env):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    sys.modules.pop("config.settings.local", None)
    return importlib.import_module("config.settings.local")


def test_local_settings_can_use_locmem_cache(monkeypatch):
    settings = reload_local_settings(monkeypatch, USE_REDIS_CACHE="False", CELERY_EAGER="False")

    assert settings.USE_REDIS_CACHE is False
    assert settings.CACHES["default"]["BACKEND"] == "django.core.cache.backends.locmem.LocMemCache"
    assert getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False) is False


def test_local_settings_can_enable_celery_eager(monkeypatch):
    settings = reload_local_settings(monkeypatch, USE_REDIS_CACHE="True", CELERY_EAGER="True")

    assert settings.CELERY_TASK_ALWAYS_EAGER is True
    assert settings.CELERY_TASK_EAGER_PROPAGATES is True
