from __future__ import absolute_import, unicode_literals

from celery import shared_task

from .models.indicators import Indicator
from .models.constructs import Construct, ConstructAssessment, ConstructResult, ConstructIndicatorResult

@shared_task
def save_indicator_results(indicatorid):
    indicator = Indicator.objects.get(id=indicatorid)
    print(f'Triggered assessment of indicator: {indicator.id} ({indicator.name})')
    indicator.save_result()

@shared_task
def save_construct_results(constructid):
    construct = Construct.objects.get(id=constructid)
    print(f'Triggered assessment of construct: {construct.id} ({construct.name})')
    construct.save_result()

# prepared for REST request
# def get_latest_assessment(constructid):
#     try:
#         construct = Construct.objects.get(id=constructid)
#     except Construct.DoesNotExist:
#         raise Exception(f'Construct with id {constructid} does not exist')
#
#     construct_assessments = ConstructAssessment.objects.filter(construct=construct)
#     if not (construct_assessments):
#         raise Exception(f'Construct with id {constructid} does not have any assessments yet')
#
#     latest_assessment = construct_assessments.latest('time_created')
#
#     return latest_assessment

