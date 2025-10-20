import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'start_project.settings')

app = Celery('start_project')
app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.broker_url = "redis://127.0.0.1:6379/0"      # broker


app.autodiscover_tasks()

# celery start command 
# To start the Celery worker, run the following command in your terminal:
# celery -A start_project worker --loglevel=info
# To start the Celery beat scheduler, run the following command in your terminal:
# celery -A start_project beat --loglevel=info
# To start the Celery worker and beat together, you can use:
# celery -A start_project worker -B --loglevel=info
# Note: Make sure to have Redis or RabbitMQ running if you are using them as a message broker.

# start your RabbitMQ server or Redis server before running the Celery worker.
# For RabbitMQ, you can start it with:
# rabbitmq-server
# For Redis, you can start it with:
# redis-server

# Make sure to have the necessary dependencies installed in your Django project:
# pip install celery redis django-celery-beat
# or
# pip install celery[redis] django-celery-beat
# You can also configure the broker URL in your Django settings file (settings.py):