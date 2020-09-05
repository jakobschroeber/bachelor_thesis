from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
import json
from django.template.defaulttags import register
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, DeleteView

from assessment.models.constructs import Construct, ConstructIndicatorRelation, ConstructResult
from assessment.forms import ConstructForm, ConstructIndicatorRelationForm, ConstructIndicatorRelationFormSet
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from assessment.forms import CrontabScheduleForm, PeriodicTaskForm



class ConstructCreateView(FormView):
    template_name = 'constructs/construct_detail.html'
    form_class = ConstructForm
    success_url = '..'

    def form_valid(self, form):
        indicators_qs = form.cleaned_data.pop('indicators', None)
        instance = Construct.objects.create(**form.cleaned_data)
        for indicator in indicators_qs:
            instance.indicators.add(indicator)

        constructid = f"{instance.id}"

        schedule = CrontabSchedule.objects.create(
            minute='*',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        periodictask = PeriodicTask.objects.create(
            crontab=schedule,
            name=f'Assessment of construct {instance.pk} ({instance})',
            task='assessment.tasks.save_construct_results',
            args=json.dumps([constructid, ]),
            enabled=False,
        )

        instance.schedule = schedule
        instance.periodictask = periodictask
        instance.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create new construct'
        return context


class ConstructUpdateView(FormView):
    template_name = 'constructs/construct_detail.html'
    form_class = ConstructForm
    success_url = '../..'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        self.obj = get_object_or_404(Construct, id=self.kwargs.get("construct_id"))
        form_kwargs['instance'] = self.obj
        return form_kwargs

    def form_valid(self, form):
        indicators_qs = form.cleaned_data.pop('indicators', None)
        instance = form.save(commit=False)
        for indicator in indicators_qs:
            instance.indicators.add(indicator)
        instance.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update construct {self.obj.id} ({self.obj.name})'
        return context


class ConstructDeleteView(DeleteView):
    model = Construct
    success_url = '../..'
    template_name = 'constructs/construct_delete.html'

    def get_object(self):
        self.construct = get_object_or_404(Construct, id=self.kwargs.get("construct_id"))
        return self.construct

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        self.object.delete()

        try:
            schedule = CrontabSchedule.objects.get(pk=self.object.schedule.pk)
        except CrontabSchedule.DoesNotExist:
            schedule = None

        if (schedule):
            schedule.delete()

        try:
            periodictask = PeriodicTask.objects.get(pk=self.object.periodictask.pk)
        except PeriodicTask.DoesNotExist:
            periodictask = None

        if (periodictask):
            periodictask.delete()

        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete construct {self.construct.id} ({self.construct.name})'
        return context


class ConstructListView(ListView):
    columns = ['id', 'name', 'column_label', 'DIFA_reference_id', 'time_created', 'last_time_modified', 'schedule__minute', \
               'schedule__hour', 'schedule__day_of_week', 'schedule__day_of_month', 'schedule__month_of_year', 'periodictask__enabled']
    queryset = Construct.objects.select_related('schedule', 'periodictask').values(*columns)
    template_name = "constructs/construct_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        column_headers = [field.help_text for field in Construct._meta.get_fields() if field.name in self.columns]
        context['title'] = 'List of all constructs'
        context['headers'] = column_headers
        return context


class ConstructScheduleUpdateView(FormView):
    template_name = 'constructs/construct_schedule_detail.html'
    form_class = CrontabScheduleForm
    success_url = '../..'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        self.construct = get_object_or_404(Construct, id=self.kwargs.get("construct_id"))
        self.schedule = get_object_or_404(CrontabSchedule, id=self.construct.schedule.id)
        form_kwargs['instance'] = self.schedule
        return form_kwargs

    def form_valid(self, form):
        schedule = form.save(commit=False)
        schedule.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update schedule of construct {self.construct.id} ({self.construct.name})'
        return context


class ConstructStatusUpdateView(FormView):
        template_name = 'constructs/construct_status_update.html'
        form_class = PeriodicTaskForm
        success_url = '../..'

        def get_form_kwargs(self):
            form_kwargs = super().get_form_kwargs()
            self.construct = get_object_or_404(Construct, id=self.kwargs.get("construct_id"))
            self.periodictask = get_object_or_404(PeriodicTask, id=self.construct.periodictask.id)
            self.periodictask.enabled = not self.periodictask.enabled
            form_kwargs['instance'] = self.periodictask
            return form_kwargs

        def form_valid(self, form):
            periodictask = form.save(commit=False)
            periodictask.save()
            return super().form_valid(form)

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            if (self.periodictask.enabled):
                action = 'Enable'
            else:
                action = 'Disable'
            context['action'] = action
            context['title'] = f'{action} assessment for construct'
            context['indicator'] = self.construct
            return context


class ConstructIndicatorWeightUpdateView(FormView):
    model = ConstructIndicatorRelation
    template_name = "constructs/construct_indicator_weights.html"
    form_class = ConstructIndicatorRelationFormSet
    success_url = '..'
    formset_errors = None

    def get_title(self):
        self.construct = get_object_or_404(Construct, id=self.kwargs.get("construct_id"))
        title = f'Adjust weights of indicators assigned to construct {self.construct.id} ({self.construct.name})'
        return title

    def post(self, request, *args, **kwargs):
        formset = ConstructIndicatorRelationFormSet(request.POST)

        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    form.save()
                else:
                    print(form.errors)
            return self.form_valid(formset)
        self.formset_errors = formset.non_form_errors()
        print(self.formset_errors)
        return self.render_to_response({'formset': formset, 'formset_errors': self.formset_errors, 'title': self.get_title()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_title()
        qs = ConstructIndicatorRelation.objects.filter(construct=self.construct)
        formset = ConstructIndicatorRelationFormSet(queryset=qs)
        context['formset'] = formset
        context['formset_errors'] = self.formset_errors

        return context


class ConstructIndicatorValuesView(TemplateView):
    template_name = "constructs/construct_indicator_values.html"

    @register.filter
    def get_item(dictionary, key):
        return dictionary.get(key, '')

    def results(self):
        result = self.construct.provide_indicator_results()
        return result

    def get_context_data(self, **kwargs):
        self.construct = get_object_or_404(Construct, id=self.kwargs.get("construct_id"))
        context = super().get_context_data(**kwargs)
        context['title'] = f'Current indicator values of construct {self.construct.id} ({self.construct.name})'
        context['indicator_labels'] = list(self.construct.indicators.all().values_list('column_label', flat=True))
        return context


class ConstructCalculateListView(TemplateView):
    template_name = "constructs/construct_calculate.html"

    def results(self):
        _, result = self.construct.calculate_result()
        return result

    def get_context_data(self, **kwargs):
        self.construct = get_object_or_404(Construct, id=self.kwargs.get("construct_id"))
        context = super().get_context_data(**kwargs)
        context['title'] = f'Current values of construct {self.construct.id} ({self.construct.name})'
        return context


class ConstructResultsListView(ListView):
    template_name = "constructs/construct_result.html"

    def get_queryset(self):
        self.construct = get_object_or_404(Construct, id=self.kwargs.get("construct_id"))
        # construct_assessments = ConstructAssessment.objects.filter(construct=self.construct)
        queryset = ConstructResult.objects.filter(assessment__construct=self.construct).select_related('user')
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Database results of construct {self.construct.id} ({self.construct.name})'
        context['construct'] = self.construct
        return context

        # todo: add attribute exported in ListView


# todo: add ListView class for model ConstructIndicatorResult and make accessible from ConstructResultsListView