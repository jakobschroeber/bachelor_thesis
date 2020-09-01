from __future__ import absolute_import, unicode_literals

from celery import shared_task

from .models.indicators import Indicator
from .models.constructs import Construct

@shared_task
def save_indicator_results(indicatorid):
    indicator = Indicator.objects.get(id=indicatorid)
    print(f'Triggered assessment of indicator: {indicator.id} ({indicator.name})')
    indicator.save_result(minutes=indicator.minutes)

@shared_task
def save_construct_results(constructid):
    construct = Construct.objects.get(id=constructid)
    print(f'Triggered assessment of construct: {construct.id} ({construct.name})')
    construct.save_result(minutes=construct.minutes)