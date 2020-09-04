from django.db import models
from administration.models import Course, User
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from types import ModuleType


class Indicator(models.Model):
    #primary key field is automatically added
    name                = models.CharField(max_length=100, help_text = 'Indicator name')
    column_label        = models.CharField(max_length=100, help_text = 'Column label') # todo: make column_label unique=True
    code                = models.TextField(default='# Python code for indicator calculation\n\n')
    minutes             = models.BigIntegerField(help_text = 'Consider ... minutes retrospectively')
    description         = models.CharField(max_length=100, blank=True, help_text = 'Description')
    DIFA_reference_id   = models.CharField(max_length=50, blank=True, help_text = 'DIFA ID') # todo: make column_label unique=True
    time_created        = models.DateTimeField(auto_now_add=True, help_text = 'Created')
    last_time_modified  = models.DateTimeField(auto_now=True, help_text = 'Last modified')
    schedule            = models.ForeignKey(CrontabSchedule, on_delete=models.PROTECT, null=True)
    periodictask        = models.ForeignKey(PeriodicTask, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'{self.name}'

    def calculate_result(self, courses=Course.objects.exclude(format='site'), minutes=None):
        # adapted from https://stackoverflow.com/questions/5362771/how-to-load-a-module-from-code-in-a-string
        course_qs = courses.filter(ignore_activity=False)
        mod = ModuleType(f"indicator_{self.id}", f"Code for calculation of indicator with pk {self.id}")
        mod.course_qs = course_qs
        if minutes is None:
            mod.minutes = self.minutes
        else:
            mod.minutes = minutes
        exec(self.code, mod.__dict__)

        # todo: validation of dict_result needed here:
        #   - column headers have to be 'courseid', 'userid', 'value' - 3 keys only
        #   - at least two different results per course, otherwise exclude course

        return mod.dict_result


    def save_result(self, courses=Course.objects.exclude(format='site')):
        preexisting_results = IndicatorResult.objects.filter(indicator=self)
        for course in courses:
            if course.ignore_activity:
                preexisting_results.filter(course=course.pk).delete()
            else:
                preexisting_results.filter(course=course.pk).exclude(user__in=course.get_users_for_assessment()).delete()
        raw_results = self.calculate_result(courses)

        results = [
            IndicatorResult(
                indicator = self,
                course=Course.objects.get(pk=entry.get('courseid')),
                user = User.objects.get(pk=entry.get('userid')),
                value = entry.get('value')
            )
            for entry in raw_results
        ]
        IndicatorResult.objects.bulk_create(results, batch_size=200)


class IndicatorResult(models.Model):
    indicator           = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    course              = models.ForeignKey(Course, on_delete=models.CASCADE)
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    value               = models.FloatField(null=True)
    time_created        = models.DateTimeField(auto_now_add=True)
    exported            = models.BooleanField(default=False)

    class Meta:
        ordering = ["indicator", "course", "user"]