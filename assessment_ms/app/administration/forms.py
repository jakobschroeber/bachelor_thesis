from django.forms import ModelForm, HiddenInput
from .models import Course, RoleAssignments

class CourseStatusForm(ModelForm):
    class Meta:
        model = Course
        fields = [
            'id',
            'ignore_activity'
        ]
        widgets = {
            'id': HiddenInput(),
            'ignore_activity': HiddenInput(),
        }


class RoleAssignmentsStatusForm(ModelForm):
    class Meta:
        model = RoleAssignments
        fields = [
            'id',
            'ignore_activity'
        ]
        widgets = {
            'id': HiddenInput(),
            'ignore_activity': HiddenInput(),
        }
