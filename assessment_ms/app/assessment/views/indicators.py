from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
import json
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, DeleteView

from assessment.models.indicators import Indicator, IndicatorResult
from assessment.models.constructs import Construct
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from assessment.forms import IndicatorForm, CrontabScheduleForm, PeriodicTaskForm


class IndicatorCreateView(FormView):
    template_name = 'indicators/indicator_detail.html'
    form_class = IndicatorForm
    success_url = '..'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        try:
            self.construct = Construct.objects.get(pk=self.kwargs.get('construct_id'))
        except Construct.DoesNotExist:
            self.construct = None

        return form_kwargs

    def form_valid(self, form):
        indicator = Indicator.objects.create(**form.cleaned_data)
        indicatorid = f"{indicator.id}"

        schedule = CrontabSchedule.objects.create(
            minute = '*',
            hour = '*',
            day_of_week = '*',
            day_of_month = '*',
            month_of_year = '*',
        )

        periodictask = PeriodicTask.objects.create(
            crontab = schedule,
            name = f'Assessment of indicator {indicator.pk} ({indicator})',
            task = 'assessment.tasks.save_indicator_results',
            args = json.dumps([indicatorid, ]),
            enabled = False,
        )

        indicator.schedule = schedule
        indicator.periodictask = periodictask
        indicator.save()

        if self.construct is not None:
            self.construct.indicators.add(indicator)
            self.construct.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.construct is None:
            context['title'] = 'Create new indicator'
        else:
            context['title'] = f'Create new indicator for construct {self.construct.id} ({self.construct.name})'
        return context


class IndicatorUpdateView(FormView):
    template_name = 'indicators/indicator_detail.html'
    form_class = IndicatorForm
    success_url = '../..'

    def form_valid(self, form):
        indicator = form.save(commit=False)
        indicator.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update indicator {self.indicator.id} ({self.indicator.name})'
        return context


class IndicatorDeleteView(DeleteView):
    model = Indicator
    success_url = '../..'
    template_name = 'indicators/indicator_delete.html'

    def get_object(self):
        self.indicator = get_object_or_404(Indicator, id=self.kwargs.get("indicator_id"))
        return self.indicator

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
        context['title'] = f'Delete indicator {self.indicator.id} ({self.indicator.name})'
        return context


class IndicatorListView(ListView):
    columns = ['id', 'name', 'column_label', 'DIFA_reference_id', 'time_created', 'last_time_modified', 'schedule__minute', \
               'schedule__hour', 'schedule__day_of_week', 'schedule__day_of_month', 'schedule__month_of_year', 'periodictask__enabled']
    template_name = "indicators/indicator_list.html"

    def get_queryset(self):
        try:
            self.construct = Construct.objects.get(pk=self.kwargs.get('construct_id'))
        except Construct.DoesNotExist:
            self.construct = None
            queryset = Indicator.objects.select_related('schedule', 'periodictask').values(*self.columns)
        else:
            queryset = Indicator.objects.filter(construct__pk=self.construct.pk).select_related('schedule', 'periodictask').values(*self.columns)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        column_headers = [field.help_text for field in Indicator._meta.get_fields() if field.name in self.columns]
        if self.construct is None:
            title = 'List of all indicators'
        else:
            title = f'List of indicators assigned to construct {self.construct.id} ({self.construct.name})'
        context['title'] = title
        context['headers'] = column_headers
        return context


class IndicatorScheduleUpdateView(FormView):
    template_name = 'indicators/indicator_schedule_detail.html'
    form_class = CrontabScheduleForm
    success_url = '../..'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        self.indicator = get_object_or_404(Indicator, id=self.kwargs.get("indicator_id"))
        self.schedule = get_object_or_404(CrontabSchedule, id=self.indicator.schedule.id)
        form_kwargs['instance'] = self.schedule
        return form_kwargs

    def form_valid(self, form):
        schedule = form.save(commit=False)
        schedule.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update schedule of indicator {self.indicator.id} ({self.indicator.name})'
        return context


class IndicatorStatusUpdateView(FormView):
        template_name = 'indicators/indicator_status_update.html'
        form_class = PeriodicTaskForm
        success_url = '../..'

        def get_form_kwargs(self):
            form_kwargs = super().get_form_kwargs()
            self.indicator = get_object_or_404(Indicator, id=self.kwargs.get("indicator_id"))
            self.periodictask = get_object_or_404(PeriodicTask, id=self.indicator.periodictask.id)
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
            context['title'] = f'{action} assessment for indicator'
            context['indicator'] = self.indicator
            return context


class IndicatorCalculateListView(TemplateView):
    template_name = "indicators/indicator_calculate.html"

    def results(self):
        raw_result = self.indicator.calculate_result()
        (k1, k2, k3) = raw_result[0]
        column_label = self.indicator.column_label
        result = [{'Course ID': x[k1], 'User ID': x[k2], column_label: x[k3]} for x in raw_result]
        return result

    def get_context_data(self, **kwargs):
        self.indicator = get_object_or_404(Indicator, id=self.kwargs.get("indicator_id"))
        context = super().get_context_data(**kwargs)
        context['title'] = f'Current values of indicator {self.indicator.id} ({self.indicator.name})'
        return context


class IndicatorResultsListView(ListView):
    template_name = "indicators/indicator_result.html"

    def get_queryset(self):
        self.indicator = get_object_or_404(Indicator, id=self.kwargs.get("indicator_id"))
        queryset = IndicatorResult.objects.filter(indicator=self.indicator).select_related('user')
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Database results of indicator {self.indicator.id} ({self.indicator.name})'
        context['indicator'] = self.indicator
        return context