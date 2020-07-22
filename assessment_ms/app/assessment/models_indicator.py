from django.db import models
from .models_construct import Construct
from data_sink.models import MoodleUser

from types import ModuleType
from django.utils import timezone


class Indicator(models.Model):
    #primary key field is automatically added
    name                = models.CharField(max_length=100, help_text = 'Indicator name')
    related_construct   = models.ForeignKey(Construct, on_delete=models.SET_NULL, blank=True, null=True)
    column_label        = models.CharField(max_length=100, help_text = 'Column label in database results')
    code                = models.TextField(default='# Python code for indicator calculation\n\n')
    description         = models.CharField(max_length=100, blank=True, help_text = 'Description')
    DIFA_reference_id   = models.CharField(max_length=50, blank=True, help_text = 'DIFA ID')
    time_created        = models.DateTimeField(auto_now_add=True, help_text = 'Created')
    last_time_modified  = models.DateTimeField(auto_now=True, help_text = 'Last modified')

    def __str__(self):
        return f'{self.name}'

    def calculate_result(self, userid_list):
        # adapted from https://stackoverflow.com/questions/5362771/how-to-load-a-module-from-code-in-a-string
        mod = ModuleType(f"indicator_{self.id}", f"Code for calculation of indicator with pk {self.id}")
        exec(self.code, mod.__dict__)
        # user ids are passed in as list instead of queryset because Django does not allow cross-db subqueries
        raw_result = mod.queryset.filter(userid__in=userid_list)
        # validation of queryset needed here: has to be in the format user(int), result(float) - 2 keys only
        # additional validation needed: At least one result

        # column headers are arbitrary, will be changed subsequently
        return raw_result

    def save_result(self, user_queryset):
        preexisting_results = IndicatorResult.objects.filter(indicator=self)
        preexisting_results.filter(user__in=user_queryset.filter(ignore_activity=True)).delete()
        userid_list = list(user_queryset.filter(ignore_activity=False).values_list('id', flat=True))
        raw_results = self.calculate_result(userid_list)
        # assumption here is that calculate_result() delivers validated list of dictionaries [{user: x, result: y}]
        (k1, k2) = raw_results[0]
        results = []
        for result in raw_results:
            entry, created = preexisting_results.get_or_create(
                indicator = self,
                user = MoodleUser.objects.get(pk=result.get(k1))
                )
            entry.value = result.get(k2)
            entry.last_time_modified = timezone.now()
            results.append(entry)
        preexisting_results.bulk_update(results, ['value', 'last_time_modified'], batch_size=50)


class IndicatorResult(models.Model):
    indicator           = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    user                = models.ForeignKey(MoodleUser, on_delete=models.CASCADE)
    value               = models.FloatField(null=True)
    time_created        = models.DateTimeField(auto_now_add=True)
    last_time_modified  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["indicator", "user"]
        unique_together = (("indicator", "user"),)
