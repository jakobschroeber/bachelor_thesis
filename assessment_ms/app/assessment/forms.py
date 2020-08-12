from app.forms import Html5ModelForm
from django.forms import ModelMultipleChoiceField, CheckboxSelectMultiple, TextInput
from django_ace import AceWidget # https://github.com/django-ace/django-ace

from django.utils.translation import gettext_lazy as _

from assessment.models.indicators import Indicator
from assessment.models.constructs import Construct


class IndicatorForm(Html5ModelForm):
    class Meta:
        model = Indicator
        fields = '__all__'
        widgets = {
            "code":
                AceWidget(mode='python',
                          theme='textmate',
                          width='90%',
                          usesofttabs=True,
                          tabsize=2,
                          minlines=20),
            'minutes': TextInput
        }
        labels = {
            'name': _(''),
            'column_label': _(''),
            'code': _(''),
            'description': _(''),
            'DIFA_reference_id': _(''),
            'minutes': _('')
        }

class ConstructForm(Html5ModelForm):
    indicators = ModelMultipleChoiceField(queryset = Indicator.objects.all(), widget = CheckboxSelectMultiple(),
                                                label='')
    class Meta:
        model = Construct
        fields = '__all__'
        labels = {
            'name': _(''),
            'column_label': _(''),
            'indicators': _(''),
            'description': _(''),
            'DIFA_reference_id': _(''),
        }
