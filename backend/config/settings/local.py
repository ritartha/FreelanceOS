"""
Local development settings for FreelanceOS.
"""

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

# For Docker, allow all IPs to access debug toolbar
import socket

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]

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
# Cache (use local memory in dev if Redis is unavailable)
# =============================================================================

# Override if you want to skip Redis locally:
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#     }
# }

# =============================================================================
# Celery (eager mode for easier debugging)
# =============================================================================

# Uncomment to run tasks synchronously during dev:
# CELERY_TASK_ALWAYS_EAGER = True
# CELERY_TASK_EAGER_PROPAGATES = True

# =============================================================================
# Logging
# =============================================================================

LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405
