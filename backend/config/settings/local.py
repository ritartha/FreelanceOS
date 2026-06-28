"""
Local development settings for FreelanceOS.
"""

from decouple import config

from .base import *  # noqa: F401,F403

# =============================================================================
# Debug
# =============================================================================

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# =============================================================================
# Installed Apps (Dev Extras)
# =============================================================================

INSTALLED_APPS += [  # noqa: F405
    "debug_toolbar",
    "django_extensions",
]

# =============================================================================
# Middleware (Debug Toolbar)
# =============================================================================

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# =============================================================================
# Email
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# =============================================================================
# Static Files (no manifest in dev)
# =============================================================================

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# =============================================================================
# CORS (relaxed for local dev)
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = True

# =============================================================================
# Cache
# =============================================================================

USE_REDIS_CACHE = config("USE_REDIS_CACHE", default=True, cast=bool)

if not USE_REDIS_CACHE:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# =============================================================================
# Celery — set CELERY_EAGER=True in .env to run tasks synchronously
# =============================================================================

if config("CELERY_EAGER", default=False, cast=bool):
    CELERY_TASK_ALWAYS_EAGER = True  # noqa: F405
    CELERY_TASK_EAGER_PROPAGATES = True  # noqa: F405

# =============================================================================
# Logging
# =============================================================================

LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405
