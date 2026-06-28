web: cd backend && python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
worker: cd backend && celery -A config worker -l info -Q default,emails,notifications,pdf_generation,billing,reports --concurrency=2
beat: cd backend && celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
