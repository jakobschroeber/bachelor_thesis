from __future__ import absolute_import, unicode_literals

from celery import shared_task

from celery.signals import worker_process_init
from django.db import connections

connection = connections['cassandra']

@worker_process_init.connect
def connect_db(**kwargs):
    connection.reconnect()


from assessment.models.indicators import IndicatorResult
from .models import AssessmentResult
from cassandra.cqlengine.query import BatchQuery


@shared_task
def export_indicator_results():
    export_qs = IndicatorResult.objects.filter(exported=False).values(
        'indicator_id', 'course_id', 'user_id', 'value', 'time_created')
    # with BatchQuery() as b:
    #     for result in export_qs:
    #         AssessmentResult.batch(b).using('cassandra').create(**result)
    for result in export_qs:
        AssessmentResult.objects.create(**result)
    export_qs.update(exported=True)


@shared_task
def cleanup_exported_indicator_results():
    cleanup_qs = IndicatorResult.objects.filter(exported=True)
    cleanup_qs.delete()