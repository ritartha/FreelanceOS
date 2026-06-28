# FreelanceOS

FreelanceOS is a Django-based platform for managing freelance operations, including authentication, CRM, projects, tasks, invoices, expenses, reporting, files, notifications, and background processing with Celery.

## Setup Options

### Local Python environment (recommended)

Run FreelanceOS directly from a Python virtual environment:

1. Create dependencies and bootstrap the project:
   ```bash
   make setup
   ```
   Or use the shell bootstrap:
   ```bash
   bash backend/setup.sh
   ```
2. Edit `.env` with your local database and Redis settings if needed.
3. Start infrastructure only, if you want PostgreSQL and Redis from Docker:
   ```bash
   make services-up
   ```
4. Run the Django server:
   ```bash
   make run
   ```

### Docker (alternative)

Run the full application stack in containers:

```bash
docker compose --profile docker up
```

For local Python development with only infrastructure containers:

```bash
docker compose --profile services up -d
```

## Local setup details

- Python: 3.12+
- Virtual environment path: `backend/.venv`
- Install dependencies:
  ```bash
  make install
  ```
- Run migrations:
  ```bash
  make migrate
  ```
- Create a superuser:
  ```bash
  make superuser
  ```
- Start a Celery worker:
  ```bash
  make worker
  ```
- Start Celery beat:
  ```bash
  make beat
  ```

## Key environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.settings.local` | Active Django settings module |
| `DATABASE_URL` | `******localhost:5432/freelanceos` | Database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis cache/session connection |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Celery broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | Celery result backend |
| `USE_REDIS_CACHE` | `True` | Set to `False` to use in-memory Django cache locally |
| `CELERY_EAGER` | `False` | Set to `True` to execute Celery tasks synchronously |
| `DJANGO_DEBUG` | `True` | Enables debug mode |

## Available `make` commands

| Command | Description |
| --- | --- |
| `make venv` | Create the virtual environment |
| `make install` | Install local dependencies |
| `make setup` | Install deps, copy `.env`, migrate, and create a superuser |
| `make run` | Start the Django development server |
| `make worker` | Start the Celery worker |
| `make beat` | Start the Celery beat scheduler |
| `make migrate` | Run database migrations |
| `make makemigrations` | Create new migrations |
| `make resetdb` | Drop and recreate the database |
| `make test` | Run the test suite |
| `make test-cov` | Run tests with coverage |
| `make lint` | Run flake8 |
| `make format` | Run black and isort |
| `make check-format` | Check black and isort formatting |
| `make check` | Run Django system checks |
| `make collectstatic` | Collect static files |
| `make shell` | Open `shell_plus` |
| `make show-urls` | List registered URL patterns |
| `make services-up` | Start only PostgreSQL and Redis via Docker |
| `make services-down` | Stop PostgreSQL and Redis Docker services |

## API endpoints overview

Authentication endpoints are exposed under `/api/v1/auth/`:

- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `POST /api/v1/auth/token/refresh/`
- `POST /api/v1/auth/verify-email/`
- `POST /api/v1/auth/password/reset-request/`
- `POST /api/v1/auth/password/reset/`
- `POST /api/v1/auth/password/change/`
- `GET /api/v1/auth/me/`

## Tech stack

- Django 5.1
- Django REST Framework
- PostgreSQL
- Redis
- Celery + django-celery-beat
- pytest
- flake8, black, isort
- WhiteNoise
- WeasyPrint
