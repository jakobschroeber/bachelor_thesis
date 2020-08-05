from django.db import models
from administration.models import Course, User

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

    def provide_indicator_results(self, course_qs, aggregation_type):
        indicators = self.indicator_set.all()
        indicator_results = {}

        # For each course create entries (courseid, userid) used as keys later
        for course in course_qs:
            for userid in course.get_users_for_assessment():
                indicator_results[(course.id, userid)] = {}

        # for each indicator, per course: calculate min and max and write indicator values into dictionary
        for indicator in indicators:
            column_label = indicator.column_label
            queryset = indicator.calculate_result(course_qs)
            (k1, k2, k3) = queryset[0]
            for course in course_qs:
                if (aggregation_type == 'original'):
                    for entry in queryset.filter(courseid=course.id):
                        indicator_results[(entry[k1], entry[k2])][column_label] = entry[k3]
                elif (aggregation_type == 'normalized'):
                    max = queryset.filter(courseid=course.id).aggregate(Max(k3))[f'{k3}__max']
                    min = queryset.filter(courseid=course.id).aggregate(Min(k3))[f'{k3}__min']
                    for entry in queryset.filter(courseid=course.id):
                        indicator_results[(entry[k1], entry[k2])][column_label] = (entry[k3] - min) / (max - min)
                elif (aggregation_type == 'standardized'):
                    avg = queryset.filter(courseid=course.id).aggregate(Avg(k3))[f'{k3}__avg']
                    stddev = queryset.filter(courseid=course.id).aggregate(StdDev(k3))[f'{k3}__stddev']
                    for entry in queryset.filter(courseid=course.id):
                        indicator_results[(entry[k1], entry[k2])][column_label] = (entry[k3] - avg) / stddev
                else:
                    raise('Unknown aggregation type')
        return indicator_results

    def calculate_result(self, course_qs):
        indicator_results = self.provide_indicator_results(course_qs, 'normalized') # todo: get aggregation_type from self
        column_label = self.column_label
        result = [{
            'Course ID': courseid,
            'User ID': userid,
            column_label: mean(indicator_results[(courseid, userid)][value] for value in indicator_results[(courseid, userid)])
        } for (courseid, userid) in indicator_results if any(indicator_results[(courseid, userid)])]
        return result

    def save_result(self, course_qs):
        preexisting_results = ConstructResult.objects.filter(construct=self)
        for course in course_qs:
            preexisting_results.filter(course=course.pk).exclude(user__in=course.get_users_for_assessment()).delete()
        raw_results = self.calculate_result(course_qs)
        (k1, k2, k3) = raw_results[0]
        results = []
        for result in raw_results:
            entry, created = preexisting_results.get_or_create(
                construct = self,
                course=Course.objects.get(pk=result.get(k1)),
                user = User.objects.get(pk=result.get(k2))
                )
            entry.value = result.get(k3)
            entry.last_time_modified = timezone.now()
            results.append(entry)
        preexisting_results.bulk_update(results, ['value', 'last_time_modified'], batch_size=50)


class ConstructResult(models.Model):
    construct           = models.ForeignKey(Construct, on_delete=models.CASCADE)
    course              = models.ForeignKey(Course, on_delete=models.CASCADE)
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    value               = models.FloatField(null=True)
    time_created        = models.DateTimeField(auto_now_add=True)
    last_time_modified  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["construct", "course", "user"]
        unique_together = (("construct", "course", "user"),)

    def __str__(self):
        return f'{self.construct.name}: {self.user.id}'