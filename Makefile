# =============================================================================
# FreelanceOS — Developer Makefile
# =============================================================================
# Usage: make <target>
# Requires: Python 3.12+, PostgreSQL, Redis (or USE_REDIS_CACHE=False)
# =============================================================================

PYTHON     := python3
VENV       := backend/.venv
PIP        := $(VENV)/bin/pip
MANAGE     := $(VENV)/bin/python backend/manage.py
PYTEST     := $(VENV)/bin/pytest
CELERY     := $(VENV)/bin/celery

.DEFAULT_GOAL := help

# ---- Setup ------------------------------------------------------------------

.PHONY: venv
venv:  ## Create the virtual environment
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

.PHONY: install
install: venv  ## Install all local dependencies
	$(PIP) install -r backend/requirements/local.txt

.PHONY: setup
setup: install  ## Full first-time setup: install deps, copy .env, migrate, create superuser
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env created from .env.example — edit it before continuing."; fi
	$(MANAGE) migrate
	$(MANAGE) createsuperuser

# ---- Database ---------------------------------------------------------------

.PHONY: migrate
migrate:  ## Run database migrations
	$(MANAGE) migrate

.PHONY: makemigrations
makemigrations:  ## Create new migrations
	$(MANAGE) makemigrations

.PHONY: resetdb
resetdb:  ## Drop and recreate the database (destructive!)
	$(MANAGE) reset_db --noinput
	$(MANAGE) migrate

# ---- Run --------------------------------------------------------------------

.PHONY: run
run:  ## Start the Django development server
	$(MANAGE) runserver

.PHONY: shell
shell:  ## Open the Django shell
	$(MANAGE) shell_plus

.PHONY: worker
worker:  ## Start the Celery worker
	cd backend && $(CELERY) -A config worker -l info -Q default,emails,notifications,pdf_generation,billing,reports

.PHONY: beat
beat:  ## Start the Celery beat scheduler
	cd backend && $(CELERY) -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# ---- Testing ----------------------------------------------------------------

.PHONY: test
test:  ## Run the test suite
	cd backend && $(PYTEST)

.PHONY: test-cov
test-cov:  ## Run tests with coverage report
	cd backend && $(PYTEST) --cov=apps --cov-report=term-missing --cov-report=html

# ---- Code Quality -----------------------------------------------------------

.PHONY: lint
lint:  ## Run flake8 linter
	$(VENV)/bin/flake8 backend/

.PHONY: format
format:  ## Auto-format code with black and isort
	$(VENV)/bin/black backend/
	$(VENV)/bin/isort backend/

.PHONY: check-format
check-format:  ## Check formatting without making changes
	$(VENV)/bin/black --check backend/
	$(VENV)/bin/isort --check-only backend/

# ---- Django Utilities -------------------------------------------------------

.PHONY: collectstatic
collectstatic:  ## Collect static files
	$(MANAGE) collectstatic --noinput

.PHONY: check
check:  ## Run Django system checks
	$(MANAGE) check

.PHONY: superuser
superuser:  ## Create a superuser interactively
	$(MANAGE) createsuperuser

.PHONY: show-urls
show-urls:  ## List all registered URL patterns
	$(MANAGE) show_urls

# ---- Docker (infrastructure only) ------------------------------------------

.PHONY: services-up
services-up:  ## Start only PostgreSQL + Redis via Docker (no Django container)
	docker compose up postgres redis -d

.PHONY: services-down
services-down:  ## Stop PostgreSQL + Redis Docker services
	docker compose stop postgres redis

# ---- Help -------------------------------------------------------------------

.PHONY: help
help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
