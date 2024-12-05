Запуск Flower: celery -A celery_worker.celery flower --port=5555 --broker=redis://localhost:6377/0

Запуск worker: celery -A celery_worker.celery worker --loglevel=info -Q work  

Запуск Celery beat: celery -A celery_worker.celery beat --loglevel=info
