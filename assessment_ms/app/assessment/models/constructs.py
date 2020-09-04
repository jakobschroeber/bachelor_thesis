from django.db import models
from assessment.models.indicators import Indicator, IndicatorResult
from administration.models import Course, User
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from enum import Enum
import pandas as pd
from sklearn import preprocessing
from statistics import mean


class Scaler(Enum):
    NoScaler            = "No scaler"
    MinMaxScaler        = "MinMaxScaler"
    MaxAbsScaler        = "MaxAbsScaler"
    StandardScaler      = "StandardScaler"
    RobustScaler        = "RobustScaler"
    Normalizer          = "Normalizer"
    QuantileTransformer = "QuantileTransformer"
    PowerTransformer    = "PowerTransformer"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class Construct(models.Model):
    # primary key field is automatically added
    name                = models.CharField(max_length=100, help_text = 'Construct name')
    indicators          = models.ManyToManyField(Indicator, through='ConstructIndicatorRelation', blank=True)
    column_label        = models.CharField(max_length=100, help_text = 'Column label in database results') # todo: make unique=True
    minutes             = models.BigIntegerField(help_text = 'Consider ... minutes retrospectively')
    scaler              = models.CharField(max_length=255, choices=Scaler.choices(), default='NoScaler')
    description         = models.CharField(max_length=100, blank=True, help_text = 'Description')
    DIFA_reference_id   = models.CharField(max_length=50, blank=True, help_text = 'DIFA ID')
    time_created        = models.DateTimeField(auto_now_add=True, help_text = 'Created')
    last_time_modified  = models.DateTimeField(auto_now=True, help_text = 'Last modified')
    schedule            = models.ForeignKey(CrontabSchedule, on_delete=models.PROTECT, null=True)
    periodictask        = models.ForeignKey(PeriodicTask, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.name}'

    def getscaler(self, scalername=None):
        if scalername is None:
            scalername = self.scaler
        return {
            'NoScaler': None,
            'MinMaxScaler': preprocessing.MinMaxScaler(),
            'MaxAbsScaler': preprocessing.MaxAbsScaler(),
            'StandardScaler': preprocessing.StandardScaler(),
            'RobustScaler': preprocessing.RobustScaler(),
            'Normalizer': preprocessing.Normalizer(),
            'QuantileTransformer': preprocessing.QuantileTransformer(),
            'PowerTransformer': preprocessing.PowerTransformer()
        }.get(scalername)

    def provide_indicator_results(self, courses=Course.objects.exclude(format='site')):
        course_qs = courses.filter(ignore_activity=False)
        indicators = self.indicators.all()
        indicator_results_dict = {}

        scaler = self.getscaler()
        print(scaler)

        # For each course create key (courseid, userid)
        for course in course_qs:
            for userid in course.get_users_for_assessment():
                indicator_results_dict[(course.id, userid)] = {}

        # for each indicator, per course: calculate indicator values and store as key-value pair into indicator_results_dict[(courseid, userid)]
        for indicator in indicators:
            column_label = indicator.column_label

            for course in course_qs:
                raw_results = indicator.calculate_result(course_qs.filter(id=course.id), self.minutes)

                if scaler is not None:
                    df = pd.DataFrame(raw_results)
                    df[['value',]] = scaler.fit_transform(df[['value',]])
                    indicator_inner_results = df.to_dict('records')
                else:
                    indicator_inner_results = raw_results

                for entry in indicator_inner_results:
                    indicator_results_dict[(entry['courseid'], entry['userid'])][column_label] = entry['value']

        print(indicator_results_dict)
        return indicator_results_dict

    def calculate_result(self, courses=Course.objects.exclude(format='site')):
        indicator_results = self.provide_indicator_results(courses)
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