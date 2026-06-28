"""
Production settings for FreelanceOS.
Optimised for Railway deployment.
"""

import os

from decouple import config

from .base import *  # noqa: F401,F403

# =============================================================================
# Security
# =============================================================================

DEBUG = False

SECRET_KEY = config("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")]
)

# Railway sets this for the running service port;
# gunicorn should bind to $PORT.
PORT = config("PORT", default="8000")
RAILWAY_ENVIRONMENT = config("RAILWAY_ENVIRONMENT", default="")
IS_RAILWAY = bool(RAILWAY_ENVIRONMENT)

# Railway terminates SSL at the proxy layer — do NOT redirect to HTTPS here
# as it causes infinite redirect loops.
# Trust the forwarded proto header instead.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HSTS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# =============================================================================
# Database Connection Pooling
# =============================================================================

DATABASES["default"]["CONN_MAX_AGE"] = 600  # noqa: F405
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # noqa: F405

# =============================================================================
# Static Files (WhiteNoise — Railway has no dedicated static server)
# =============================================================================

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Ensure collectstatic doesn't fail
# if the local static source dir doesn't exist.
STATICFILES_DIRS = [
    d for d in STATICFILES_DIRS if os.path.isdir(d)  # noqa: F405
]

# =============================================================================
# Sentry (optional — set SENTRY_DSN in Railway env vars)
# =============================================================================

SENTRY_DSN = config("SENTRY_DSN", default="")

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=config("RAILWAY_ENVIRONMENT", default="production"),
    )

# =============================================================================
# Logging (structured JSON for production)
# =============================================================================

LOGGING["formatters"]["json"] = {  # noqa: F405
    "()": "django.utils.log.ServerFormatter",
    "format": "[{server_time}] {message}",
    "style": "{",
}

# =============================================================================
# Email
# =============================================================================

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)

# =============================================================================
# DRF (disable browsable API in production)
# =============================================================================

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
]
