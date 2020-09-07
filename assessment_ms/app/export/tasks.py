from __future__ import absolute_import, unicode_literals

from celery import shared_task
from django.db import transaction

from celery.signals import worker_process_init
from .db import update_connections
from django.db import connections

import logging

from assessment.models.indicators import IndicatorResult
from assessment.models.constructs import ConstructAssessment, ConstructResult, ConstructIndicatorResult
from .models import IndicatorResultExport, AssessmentExport, ConstructResultExport, ConstructIndicatorResultExport


update_connections()
connection = connections['cassandra']

@worker_process_init.connect
def connect_db(**kwargs):
    connection.reconnect()


log = logging.getLogger(__name__)


@shared_task
def export_indicator_results():
    update_connections()
    with transaction.atomic(using='default'):
        log.info(f'Starting export of indicator results ...')
        export_qs = IndicatorResult.objects.filter(exported=False).values(
            'indicator_id', 'course_id', 'user_id', 'value', 'time_created')
        with transaction.atomic(using='cassandra'):
            for result in export_qs:
                IndicatorResultExport.objects.create(**result)
        export_qs.update(exported=True)
    log.info(f'Completed export of indicator results')

@shared_task
def cleanup_exported_indicator_results():
    with transaction.atomic(using='default'):
        log.info(f'Starting clean-up of indicator results ...')
        cleanup_qs = IndicatorResult.objects.filter(exported=True)
        cleanup_qs.delete()
    log.info(f'Completed clean-up of indicator results')

@shared_task
def export_construct_assessments():
    update_connections()
    with transaction.atomic(using='default'):
        log.info(f'Starting export of construct assessments ...')
        construct_assessment_export_qs = ConstructAssessment.objects.filter(exported=False).values(
            'construct_id', 'time_created')
        construct_result_export_qs = ConstructResult.objects.filter(exported=False).values(
            'assessment_id', 'course_id', 'user_id', 'value', 'time_created')
        construct_indicator_result_export_qs = ConstructIndicatorResult.objects.filter(exported=False).values(
            'constructresult_id', 'indicator_id', 'course_id', 'user_id', 'value', 'time_created')

        with transaction.atomic(using='cassandra'):
            for result in construct_assessment_export_qs:
                AssessmentExport.objects.create(**result)
            for result in construct_result_export_qs:
                ConstructResultExport.objects.create(**result)
            for result in construct_indicator_result_export_qs:
                ConstructIndicatorResultExport.objects.create(**result)

        construct_assessment_export_qs.update(exported=True)
        construct_result_export_qs.update(exported=True)
        construct_indicator_result_export_qs.update(exported=True)
    log.info(f'Completed export of construct assessments')

@shared_task
def cleanup_exported_construct_assessments():
    with transaction.atomic(using='default'):
        log.info(f'Starting clean-up of construct assessments ...')
        construct_assessment_cleanup_qs = ConstructAssessment.objects.filter(exported=True)
        construct_result_cleanup_qs = ConstructResult.objects.filter(exported=True)
        construct_indicator_cleanup_qs = ConstructIndicatorResult.objects.filter(exported=True)

        construct_assessment_cleanup_qs.delete()
        construct_result_cleanup_qs.delete()
        construct_indicator_cleanup_qs.delete()
    log.info(f'Completed clean-up of construct assessments')