from django.db import models
from data_sink.models import MoodleUser

from django.db.models import Avg, Max, Min
from django.db.models.aggregates import StdDev
from statistics import mean

from django.utils import timezone


class Construct(models.Model):
    # primary key field is automatically added
    name                = models.CharField(max_length=100, help_text = 'Construct name')
    column_label        = models.CharField(max_length=100, help_text = 'Column label in database results')
    description         = models.CharField(max_length=100, blank=True, help_text = 'Description')
    DIFA_reference_id   = models.CharField(max_length=50, blank=True, help_text = 'DIFA ID')
    time_created        = models.DateTimeField(auto_now_add=True, help_text = 'Created')
    last_time_modified  = models.DateTimeField(auto_now=True, help_text = 'Last modified')

    def __str__(self):
        return f'{self.name}'

    def provide_indicator_results(self, userid_list):
        indicators = self.indicator_set.all()
        indicator_results = {}
        for userid in userid_list:
            indicator_results[userid] = {}
        for indicator in indicators:
            column_label = indicator.column_label
            queryset = indicator.calculate_result(userid_list)
            (k1, k2) = queryset[0]
            for entry in queryset:
                indicator_results[entry[k1]][column_label] = entry[k2]
        return indicator_results

    def provide_standardized_indicator_results(self, userid_list):
        indicators = self.indicator_set.all()
        indicator_results = {}
        for userid in userid_list:
            indicator_results[userid] = {}
        for indicator in indicators:
            column_label = indicator.column_label
            queryset = indicator.calculate_result(userid_list)
            (k1, k2) = queryset[0]
            avg = queryset.aggregate(Avg(k2))[f'{k2}__avg']
            stddev = queryset.aggregate(StdDev(k2))[f'{k2}__stddev']
            for entry in queryset:
                indicator_results[entry[k1]][column_label] = (entry[k2] - avg) / stddev
        return indicator_results

    def provide_normalized_indicator_results(self, userid_list): # parametrize these 3 functions to reduce redundancy
        indicators = self.indicator_set.all()
        indicator_results = {}
        for userid in userid_list:
            indicator_results[userid] = {}
        for indicator in indicators:
            column_label = indicator.column_label
            queryset = indicator.calculate_result(userid_list)
            (k1, k2) = queryset[0]
            max = queryset.aggregate(Max(k2))[f'{k2}__max']
            min = queryset.aggregate(Min(k2))[f'{k2}__min']
            for entry in queryset:
                indicator_results[entry[k1]][column_label] = (entry[k2] - min) / (max - min)
        return indicator_results

    def calculate_result(self, userid_list):
        indicator_results = self.provide_normalized_indicator_results(userid_list)
        column_label = self.column_label
        result = [{
            'user': userid,
            column_label: mean(indicator_results[userid][value] for value in indicator_results[userid])
        } for userid in userid_list if any(indicator_results[userid])]
        return result

    def save_result(self, user_queryset):
        preexisting_results = ConstructResult.objects.filter(construct=self)
        preexisting_results.filter(user__in=user_queryset.filter(ignore_activity=True)).delete()
        userid_list = list(user_queryset.filter(ignore_activity=False).values_list('id', flat=True))
        raw_results = self.calculate_result(userid_list)
        # assumption here is that calculate_result() delivers validated list of dictionaries [{user: x, result: y}]
        (k1, k2) = raw_results[0]
        results = []
        for result in raw_results:
            entry, created = preexisting_results.get_or_create(
                construct = self,
                user = MoodleUser.objects.get(pk=result.get(k1))
                )
            entry.value = result.get(k2)
            entry.last_time_modified = timezone.now()
            results.append(entry)
        preexisting_results.bulk_update(results, ['value', 'last_time_modified'], batch_size=50)


class ConstructResult(models.Model):
    construct           = models.ForeignKey(Construct, on_delete=models.CASCADE)
    user                = models.ForeignKey(MoodleUser, on_delete=models.CASCADE)
    value               = models.FloatField(null=True)
    time_created        = models.DateTimeField(auto_now_add=True)
    last_time_modified  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["construct", "user"]
        unique_together = (("construct", "user"),)

    def __str__(self):
        return f'{self.construct.name}: {self.user.id}'