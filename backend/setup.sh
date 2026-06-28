#!/usr/bin/env bash
# =============================================================================
# FreelanceOS — Local Development Bootstrap Script
# =============================================================================
# Run from the repo root: bash backend/setup.sh
# =============================================================================

set -euo pipefail

PYTHON=${PYTHON:-python3}
VENV=backend/.venv

echo "==> Checking Python version..."
$PYTHON --version

echo "==> Creating virtual environment at $VENV..."
$PYTHON -m venv $VENV

echo "==> Activating virtual environment..."
source $VENV/bin/activate

echo "==> Upgrading pip..."
pip install --upgrade pip

echo "==> Installing dependencies..."
pip install -r backend/requirements/local.txt

echo "==> Copying .env.example to .env (if not already present)..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "    .env created — edit it with your local DB/Redis credentials before continuing."
    echo "    Press Enter when ready..."
    read -r
fi

echo "==> Running migrations..."
cd backend
python manage.py migrate

echo "==> Creating superuser..."
python manage.py createsuperuser

echo ""
echo "================================================================"
echo "  Setup complete! To start the dev server:"
echo ""
echo "    source backend/.venv/bin/activate"
echo "    cd backend"
echo "    python manage.py runserver"
echo ""
echo "  Or from repo root:  make run"
echo "================================================================"
