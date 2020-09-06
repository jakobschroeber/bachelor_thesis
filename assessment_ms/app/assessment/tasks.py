from __future__ import absolute_import, unicode_literals

from celery import shared_task
from app.settings import env
from django.db import transaction

from .models.indicators import Indicator
from .models.constructs import Construct

@shared_task(time_limit=int(env('DJANGO_ASSESSMENT_TIME_LIMIT')))
def save_indicator_results(indicatorid):
    with transaction.atomic(using='moodle'):
        indicator = Indicator.objects.get(id=indicatorid)
        with transaction.atomic(using='moodle'):
            print(f'Starting assessment of indicator: {indicator.id} ({indicator.name}) ...')
            indicator.save_result()
        print(f'Completed assessment of indicator: {indicator.id} ({indicator.name})')


@shared_task(time_limit=int(env('DJANGO_ASSESSMENT_TIME_LIMIT')))
def save_construct_results(constructid):
    with transaction.atomic(using='moodle'):
        construct = Construct.objects.get(id=constructid)
        with transaction.atomic(using='moodle'):
            print(f'Starting assessment of construct: {construct.id} ({construct.name}) ...')
            construct.save_result()
        print(f'Completed assessment of construct: {construct.id} ({construct.name})')
