from django.forms import ModelForm, HiddenInput
from .models import RoleAssignments

class RoleAssignmentsForm(ModelForm):
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
