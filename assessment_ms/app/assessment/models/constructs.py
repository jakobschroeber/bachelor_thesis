from django.db import models
from assessment.models.indicators import Indicator, IndicatorResult
from administration.models import Course, User
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from django.db.models import Avg, Max, Min
from django.db.models.aggregates import StdDev
from statistics import mean

from django.utils import timezone


class Construct(models.Model):
    # primary key field is automatically added
    name                = models.CharField(max_length=100, help_text = 'Construct name')
    indicators          = models.ManyToManyField(Indicator, through='ConstructIndicatorRelation', blank=True)
    column_label        = models.CharField(max_length=100, help_text = 'Column label in database results')
    minutes             = models.BigIntegerField(help_text = 'Consider ... minutes retrospectively')
    description         = models.CharField(max_length=100, blank=True, help_text = 'Description')
    DIFA_reference_id   = models.CharField(max_length=50, blank=True, help_text = 'DIFA ID')
    time_created        = models.DateTimeField(auto_now_add=True, help_text = 'Created')
    last_time_modified  = models.DateTimeField(auto_now=True, help_text = 'Last modified')
    schedule            = models.ForeignKey(CrontabSchedule, on_delete=models.PROTECT, null=True)
    periodictask        = models.ForeignKey(PeriodicTask, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.name}'

    def provide_indicator_results(self, aggregation_type, courses=Course.objects.exclude(format='site'), minutes=518400):
        course_qs = courses.filter(ignore_activity=False)
        indicators = self.indicators.all()
        indicator_results = {}

        # For each course create entries (courseid, userid) used as keys later
        for course in course_qs:
            for userid in course.get_users_for_assessment():
                indicator_results[(course.id, userid)] = {}

        # for each indicator, per course: calculate min and max and write indicator values into dictionary
        for indicator in indicators:
            column_label = indicator.column_label
            queryset = IndicatorResult.objects.filter(
                course__in=course_qs, indicator=indicator).values('course','user', 'value')
            for course in course_qs:
                if (aggregation_type == 'original'):
                    for entry in queryset.filter(course=course.id, user__in=course.get_users_for_assessment()):
                        indicator_results[(entry['course'], entry['user'])][column_label] = entry['value']
                elif (aggregation_type == 'normalized'):
                    max = queryset.filter(course=course.id).aggregate(Max('value'))['value__max']
                    min = queryset.filter(course=course.id).aggregate(Min('value'))['value__min']
                    # todo: verify that max and min are not None
                    range = max - min
                    for entry in queryset.filter(course=course.id, user__in=course.get_users_for_assessment()):
                        indicator_results[(entry['course'], entry['user'])][column_label] = \
                            (entry['value'] - min) / (range) if (range != 0) else 0.0
                    # else:
                    #     raise Exception(f'range of values for indicator {indicator.id} ({indicator.name}) is zero')
                elif (aggregation_type == 'standardized'):
                    avg = queryset.filter(course=course.id).aggregate(Avg('value'))['value__avg']
                    stddev = queryset.filter(course=course.id).aggregate(StdDev('value'))['value__stddev']
                    # todo: verify that avg and stddev are not None
                    for entry in queryset.filter(course=course.id, user__in=course.get_users_for_assessment()):
                        indicator_results[(entry['course'], entry['user'])][column_label] = \
                            (entry['value'] - avg) / stddev if (stddev != 0) else 0.0
                else:
                    raise('Unknown aggregation type')
        return indicator_results

    def calculate_result(self, courses=Course.objects.exclude(format='site'), minutes=518400):
        indicator_results = self.provide_indicator_results('normalized', courses, minutes) # todo: get aggregation_type from self
        result = [{
            'courseid': courseid,
            'userid': userid,
            self.column_label: mean(indicator_results[(courseid, userid)][value] for value in indicator_results[(courseid, userid)])
        } for (courseid, userid) in indicator_results if any(indicator_results[(courseid, userid)])]
        return result

    def save_result(self, courses=Course.objects.exclude(format='site'), minutes=518400):
        preexisting_results = ConstructResult.objects.filter(construct=self)
        for course in courses:
            if course.ignore_activity:
                preexisting_results.filter(course=course.pk).delete()
            else:
                preexisting_results.filter(course=course.pk).exclude(user__in=course.get_users_for_assessment()).delete()
        raw_results = self.calculate_result(courses, minutes)

        results = [
            ConstructResult(
                construct = self,
                course=Course.objects.get(pk=entry.get('courseid')),
                user = User.objects.get(pk=entry.get('userid')),
                value = entry.get(self.column_label)
            )
            for entry in raw_results
        ]
        ConstructResult.objects.bulk_create(results, batch_size=200)


class ConstructIndicatorRelation(models.Model):
    construct   = models.ForeignKey(Construct, on_delete=models.CASCADE)
    indicator   = models.ForeignKey(Indicator, on_delete=models.CASCADE)


class ConstructResult(models.Model):
    construct           = models.ForeignKey(Construct, on_delete=models.CASCADE)
    course              = models.ForeignKey(Course, on_delete=models.CASCADE)
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    value               = models.FloatField(null=True)
    time_created        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["construct", "course", "user"]

    def __str__(self):
        return f'{self.construct.name}: {self.user.id}'