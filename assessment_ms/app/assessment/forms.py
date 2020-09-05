from app.forms import Html5ModelForm
from django.forms import CharField, ModelMultipleChoiceField, CheckboxSelectMultiple, TextInput, HiddenInput, \
    NumberInput, modelformset_factory, BaseModelFormSet, ValidationError
from django_ace import AceWidget # https://github.com/django-ace/django-ace

from django.utils.translation import gettext_lazy as _

from assessment.models.indicators import Indicator
from assessment.models.constructs import Construct, ConstructIndicatorRelation
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class IndicatorForm(Html5ModelForm):
    class Meta:
        model = Indicator
        exclude = ['schedule', 'periodictask']
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
    indicators = ModelMultipleChoiceField(queryset=Indicator.objects.all(), widget=CheckboxSelectMultiple(),
                                          label='')
    class Meta:
        model = Construct
        exclude = ['schedule', 'periodictask']
        widgets = {
            'minutes': TextInput
        }
        labels = {
            'name': _(''),
            'column_label': _(''),
            'indicators': _(''),
            'scaler': _(''),
            'description': _(''),
            'DIFA_reference_id': _(''),
            'minutes': _('')
        }

class CrontabScheduleForm(Html5ModelForm):
    class Meta:
        model = CrontabSchedule
        fields = '__all__'
        labels = {
            'minute': _(''),
            'hour': _(''),
            'day_of_week': _(''),
            'day_of_month': _(''),
            'month_of_year': _('')
        }

class PeriodicTaskForm(Html5ModelForm):
    class Meta:
        model = PeriodicTask
        fields = [
            'id',
            'enabled'
        ]
        widgets = {
            'id': HiddenInput(),
            'enabled': HiddenInput(),
        }
        labels = {
            'crontab': _(''),
            'name': _(''),
            'task': _(''),
            'enabled': _('')
        }


class ConstructIndicatorRelationForm(Html5ModelForm):
    indicator = CharField(disabled=True)
    class Meta:
        model = ConstructIndicatorRelation
        fields = [
            'id',
            'weight'
        ]
        widgets = {
            'id': HiddenInput()
        }
        labels = {
            'id': _(''),
            'weight': _('')
        }


class BaseConstructIndicatorRelationFormSet(BaseModelFormSet):
    def clean(self):
        super(BaseConstructIndicatorRelationFormSet, self).clean()

        weight_sum = 0.0
        for form in self.forms:
            weight = form.cleaned_data['weight']
            weight_sum += weight
        if weight_sum > 1.0 or weight_sum < 1.0:
            raise ValidationError('The weights do not sum up to 1.0')


ConstructIndicatorRelationFormSet = modelformset_factory(ConstructIndicatorRelation, formset=BaseConstructIndicatorRelationFormSet,
         extra=0, fields=('id', 'weight'), labels = {'id': _(''), 'weight': _('')}, widgets = {
        'weight': NumberInput(attrs={'class': "weight_value"}), 'id': HiddenInput()})