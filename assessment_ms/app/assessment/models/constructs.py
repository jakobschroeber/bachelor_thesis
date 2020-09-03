from django.db import models
from assessment.models.indicators import Indicator, IndicatorResult
from administration.models import Course, User
from django_celery_beat.models import CrontabSchedule, PeriodicTask

import numpy as np
from django.db.models import Avg, Max, Min
from django.db.models.aggregates import StdDev
from statistics import mean


class Construct(models.Model):
    # primary key field is automatically added
    name                = models.CharField(max_length=100, help_text = 'Construct name')
    indicators          = models.ManyToManyField(Indicator, through='ConstructIndicatorRelation', blank=True)
    column_label        = models.CharField(max_length=100, help_text = 'Column label in database results') # todo: make unique=True
    minutes             = models.BigIntegerField(help_text = 'Consider ... minutes retrospectively')
    description         = models.CharField(max_length=100, blank=True, help_text = 'Description')
    DIFA_reference_id   = models.CharField(max_length=50, blank=True, help_text = 'DIFA ID')
    time_created        = models.DateTimeField(auto_now_add=True, help_text = 'Created')
    last_time_modified  = models.DateTimeField(auto_now=True, help_text = 'Last modified')
    schedule            = models.ForeignKey(CrontabSchedule, on_delete=models.PROTECT, null=True)
    periodictask        = models.ForeignKey(PeriodicTask, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.name}'

    def provide_indicator_results(self, aggregation_type, courses=Course.objects.exclude(format='site')):
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

            for course in course_qs:
                raw_results = indicator.calculate_result(course_qs.filter(id=course.id))

                if (aggregation_type == 'original'):
                    for entry in raw_results:
                        indicator_results[(entry['courseid'], entry['userid'])][column_label] = entry['value']
                elif (aggregation_type == 'normalized'):
                    max = np.array([entry['value'] for entry in raw_results if 'value' in entry]).max()
                    min = np.array([entry['value'] for entry in raw_results if 'value' in entry]).min()
                    if (max is not None and min is not None):
                        range = max - min
                        for entry in raw_results:
                            indicator_results[(entry['courseid'], entry['userid'])][column_label] = \
                                (entry['value'] - min) / (range) if (range != 0) else 0.0
                    else:
                        raise Exception(f'max or min for results of indicator {indicator.id} ({indicator.name}) are ' +
                                        f'None, there may be no Indicator results')
                elif (aggregation_type == 'standardized'):
                    avg = np.array([entry['value'] for entry in raw_results if 'value' in entry]).mean()
                    stddev = np.array([entry['value'] for entry in raw_results if 'value' in entry]).std()
                    # todo: verify that avg and stddev are not None
                    for entry in raw_results:
                        indicator_results[(entry['courseid'], entry['userid'])][column_label] = \
                            (entry['value'] - avg) / stddev if (stddev != 0) else 0.0
                else:
                    raise Exception('Unknown aggregation type')
        return indicator_results

    def calculate_result(self, courses=Course.objects.exclude(format='site')):
        indicator_results = self.provide_indicator_results('normalized', courses) # todo: get aggregation_type from self
        construct_result = [{
            'courseid': courseid,
            'userid': userid,
            self.column_label: mean(indicator_results[(courseid, userid)][value] for value in indicator_results[(courseid, userid)])
        } for (courseid, userid) in indicator_results if any(indicator_results[(courseid, userid)])]
        return indicator_results, construct_result

    def save_result(self, courses=Course.objects.exclude(format='site')):
        preexisting_construct_results           = ConstructResult.objects.select_related('assessment').filter(assessment__construct=self)
        preexisting_construct_indicator_results = ConstructIndicatorResult.objects.select_related('construct_result').filter(construct_result__assessment__construct=self)
        for course in courses:
            if course.ignore_activity:
                preexisting_construct_results.filter(course=course.pk).delete()
                preexisting_construct_indicator_results.filter(course=course.pk).delete()
            else:
                preexisting_construct_results.filter(course=course.pk).exclude(user__in=course.get_users_for_assessment()).delete()
                preexisting_construct_indicator_results.filter(course=course.pk).exclude(user__in=course.get_users_for_assessment()).delete()

        raw_indicator_results, raw_construct_results = self.calculate_result(courses)

        current_assessment = ConstructAssessment.objects.create(construct=self)

        construct_results = [
            ConstructResult(
                assessment = current_assessment,
                course=Course.objects.get(pk=entry['courseid']),
                user = User.objects.get(pk=entry['userid']),
                value = entry[self.column_label]
            )
            for entry in raw_construct_results
        ]
        ConstructResult.objects.bulk_create(construct_results, batch_size=200)

        stored_construct_results = ConstructResult.objects.filter(assessment = current_assessment)

        indicator_results = []
        for (courseid, userid) in raw_indicator_results:
            course = Course.objects.get(pk=courseid)
            user = User.objects.get(pk=userid)
            for column_label in raw_indicator_results[(courseid, userid)]:
                entry = ConstructIndicatorResult(
                    construct_result=stored_construct_results.get(course=course, user=user),
                    indicator=Indicator.objects.get(column_label=column_label),
                    course=course,
                    user=user,
                    value=raw_indicator_results[(courseid, userid)][column_label]
                )
                indicator_results.append(entry)

        ConstructIndicatorResult.objects.bulk_create(indicator_results, batch_size=200)


class ConstructIndicatorRelation(models.Model):
    construct   = models.ForeignKey(Construct, on_delete=models.CASCADE)
    indicator   = models.ForeignKey(Indicator, on_delete=models.CASCADE)


class ConstructAssessment(models.Model):
    construct       = models.ForeignKey(Construct, on_delete=models.CASCADE)
    time_created    = models.DateTimeField(auto_now_add=True)

    # todo: create clean-up job for old assessments

class ConstructResult(models.Model):
    assessment          = models.ForeignKey(ConstructAssessment, on_delete=models.CASCADE)
    course              = models.ForeignKey(Course, on_delete=models.CASCADE)
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    value               = models.FloatField(null=True)
    time_created        = models.DateTimeField(auto_now_add=True)
    exported = models.BooleanField(default=False)

    class Meta:
        ordering = ["assessment", "course", "user"]


class ConstructIndicatorResult(models.Model):
    construct_result    = models.ForeignKey(ConstructResult, related_name='measures', on_delete=models.CASCADE)
    indicator           = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    course              = models.ForeignKey(Course, on_delete=models.CASCADE)
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    value               = models.FloatField(null=True)
    time_created        = models.DateTimeField(auto_now_add=True) # todo: remove column time_created from models ConstructResult and ConstructIndicatorResult
    exported            = models.BooleanField(default=False)

    class Meta:
        ordering = ["construct_result", "course", "user"]

    # todo: add attribute exported to model and in ListView