from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView

from .models_indicator import Indicator, IndicatorResult
from .models_construct import Construct
from data_sink.models import MoodleUser
from .forms import IndicatorForm


class IndicatorCreateView(FormView):
    template_name = 'indicators/indicator_detail.html'
    form_class = IndicatorForm
    success_url = '..'

    def form_valid(self, form):
        Indicator.objects.create(**form.cleaned_data)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create new indicator'
        return context


class IndicatorUpdateView(FormView):
    template_name = 'indicators/indicator_detail.html'
    form_class = IndicatorForm
    success_url = '..'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        self.indicator = get_object_or_404(Indicator, id=self.kwargs.get("indicator_id"))
        form_kwargs['instance'] = self.indicator
        return form_kwargs

    def form_valid(self, form):
        indicator = form.save(commit=False)
        indicator.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update indicator {self.indicator.id} ({self.indicator.name})'
        return context


class IndicatorListView(ListView):
    columns = ['id', 'name', 'column_label', 'DIFA_reference_id', 'time_created', 'last_time_modified']
    template_name = "indicators/indicator_list.html"

    def get_queryset(self):
        try:
            self.construct = Construct.objects.get(pk=self.kwargs.get('construct_id'))
        except Construct.DoesNotExist:
            self.construct = None
            queryset = Indicator.objects.values(*self.columns)
        else:
            queryset = Indicator.objects.filter(related_construct=self.construct.pk).values(*self.columns)
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


class IndicatorCalculateListView(TemplateView):
    template_name = "indicators/indicator_calculate.html"

    def results(self):
        userid_list = list(MoodleUser.objects.filter(ignore_activity=False).values_list('id', flat=True))
        raw_result = self.indicator.calculate_result(userid_list)
        (k1, k2) = raw_result[0]
        column_label = self.indicator.column_label
        result = [{'user': x[k1], column_label: x[k2]} for x in raw_result]
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
        self.indicator.save_result(MoodleUser.objects.all())  # take this out later, make it a parameter maybe
        queryset = IndicatorResult.objects.filter(indicator=self.indicator).select_related('user')
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Database results of indicator {self.indicator.id} ({self.indicator.name})'
        context['indicator'] = self.indicator
        return context