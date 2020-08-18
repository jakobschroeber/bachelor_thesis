from __future__ import absolute_import, unicode_literals

from celery import shared_task

import datetime
from django.utils import timezone
from django.db.models import Max

from .models.indicators import Indicator, IndicatorResult


@shared_task
def save_indicator_results():
    latest_results = IndicatorResult.objects.values('indicator').annotate(latest_date=Max('time_created'))
    for indicator in Indicator.objects.all():
        minutes_delta = indicator.minutes
        try:
            latest_date = latest_results.get(indicator=indicator)['latest_date']
            if (timezone.now() >= (latest_date + datetime.timedelta(minutes=(minutes_delta - 1)))):
                indicator.save_result(minutes=minutes_delta)
        except IndicatorResult.DoesNotExist:
            indicator.save_result(minutes=minutes_delta)

        # todo: find out how incorrect time difference between results can be avoided
