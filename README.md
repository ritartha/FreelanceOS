# FreelanceOS

FreelanceOS is a Django-based platform for managing freelance operations, including CRM, projects, invoicing, reporting, and asynchronous task processing with Celery.

## Local Development (Python Virtual Environment)

1. Create and activate the virtual environment:
   ```bash
   make install
   ```
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
3. Run database migrations:
   ```bash
   make migrate
   ```
4. Create a superuser:
   ```bash
   make superuser
   ```
5. Start the app:
   ```bash
   make run
   ```

Optional:
- Celery worker: `make worker`
- Celery beat: `make beat`
- Use `CELERY_EAGER=True` in `.env` to run tasks synchronously without a worker.

## Railway Deployment (Primary)

1. Push your code to GitHub.
2. In Railway, create a new project and choose **Deploy from GitHub repo**.
3. Add a **PostgreSQL** plugin (Railway auto-injects `DATABASE_URL`).
4. Add a **Redis** plugin (Railway auto-injects `REDIS_URL`).
5. Set required environment variables in the Railway dashboard:
   - `DJANGO_SETTINGS_MODULE=config.settings.production`
   - `DJANGO_SECRET_KEY=<generate a strong key>`
   - `DJANGO_ALLOWED_HOSTS=<your-app>.railway.app`
   - `CELERY_BROKER_URL=$REDIS_URL`
   - `CELERY_RESULT_BACKEND=$REDIS_URL`
6. Set the start command:
   ```bash
   cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
   ```
7. Railway will automatically deploy on each push.

### Railway Environment Variables

| Variable | Value |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `DJANGO_SECRET_KEY` | `<generate a strong key>` |
| `DJANGO_ALLOWED_HOSTS` | `<your-app>.railway.app` |
| `CELERY_BROKER_URL` | `$REDIS_URL` |
| `CELERY_RESULT_BACKEND` | `$REDIS_URL` |
| `CSRF_TRUSTED_ORIGINS` | `https://<your-app>.railway.app` |
| `CORS_ALLOWED_ORIGINS` | `https://<your-app>.railway.app` |
| `RAILWAY_ENVIRONMENT` | `production` |

### Procfile Note

This repository includes a root `Procfile` defining `web`, `worker`, and `beat` process types for Railway and other Procfile-compatible platforms.
