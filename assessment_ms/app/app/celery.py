from __future__ import absolute_import, unicode_literals

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

from app.settings import INSTALLED_APPS, BASE_DIR, env
from celery import Celery, signals
import logging, os


@signals.after_setup_logger.connect()
def logger_setup_handler(logger, **kwargs ):
  handler = logging.FileHandler(os.path.join(BASE_DIR, 'logs/celery.log'))
  handler.setLevel(env('DJANGO_LOG_LEVEL'))
  my_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') #custom formatter
  handler.setFormatter(my_formatter)
  logger.addHandler(handler)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app', broker='amqp://guest@rabbitmq:5672//')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

if __name__ == '__main__':
  app.start()
