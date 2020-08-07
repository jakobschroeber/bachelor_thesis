from django.db import models
from administration.models import Course, User

from types import ModuleType
from django.utils import timezone


class Indicator(models.Model):
    #primary key field is automatically added
    name                = models.CharField(max_length=100, help_text = 'Indicator name')
    column_label        = models.CharField(max_length=100, help_text = 'Column label in database results')
    code                = models.TextField(default='# Python code for indicator calculation\n\n')
    description         = models.CharField(max_length=100, blank=True, help_text = 'Description')
    DIFA_reference_id   = models.CharField(max_length=50, blank=True, help_text = 'DIFA ID')
    time_created        = models.DateTimeField(auto_now_add=True, help_text = 'Created')
    last_time_modified  = models.DateTimeField(auto_now=True, help_text = 'Last modified')

    def __str__(self):
        return f'{self.name}'

    def calculate_result(self, course_qs): # todo: remove parameter course_qs if no filter is required
        # adapted from https://stackoverflow.com/questions/5362771/how-to-load-a-module-from-code-in-a-string
        mod = ModuleType(f"indicator_{self.id}", f"Code for calculation of indicator with pk {self.id}")
        mod.course_qs = course_qs
        exec(self.code, mod.__dict__)

        # todo: validation of dict_result needed here:
        #   - column headers have to be 'courseid', 'userid', 'value' - 3 keys only
        #   - at least two different results per course, otherwise exclude course

        return mod.dict_result

    def save_result(self, course_qs):
        preexisting_results = IndicatorResult.objects.filter(indicator=self)
        for course in course_qs:
            preexisting_results.filter(course=course.pk).exclude(user__in=course.get_users_for_assessment()).delete()
        raw_results = self.calculate_result(course_qs)

        results = []
        for result in raw_results:
            entry, created = preexisting_results.get_or_create(
                indicator = self,
                course = Course.objects.get(pk=result.get('courseid')),
                user = User.objects.get(pk=result.get('userid'))
                )
            entry.value = result.get('value')
            entry.last_time_modified = timezone.now()
            results.append(entry)
        preexisting_results.bulk_update(results, ['value', 'last_time_modified'], batch_size=50)


class IndicatorResult(models.Model):
    indicator           = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    course              = models.ForeignKey(Course, on_delete=models.CASCADE)
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    value               = models.FloatField(null=True)
    time_created        = models.DateTimeField(auto_now_add=True)
    last_time_modified  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["indicator", "course", "user"]
        unique_together = (("indicator", "course", "user"),)