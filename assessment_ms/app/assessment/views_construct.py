from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaulttags import register
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView

from administration.signals import initialize_update_administration_data

from .models_construct import Construct, ConstructResult
from administration.models import Course, User
from .forms import ConstructForm



class ConstructCreateView(FormView):
    template_name = 'constructs/construct_detail.html'
    form_class = ConstructForm
    success_url = '..'

    def form_valid(self, form):
        indicators_qs = form.cleaned_data.pop('indicators', None)
        instance = Construct.objects.create(**form.cleaned_data)
        for indicator in indicators_qs:
            instance.indicators.add(indicator)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create new constuct'
        return context


class ConstructUpdateView(FormView):
    template_name = 'constructs/construct_detail.html'
    form_class = ConstructForm
    success_url = '..'

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


class ConstructListView(ListView):
    columns = ['id', 'name', 'column_label', 'DIFA_reference_id', 'time_created', 'last_time_modified']
    queryset = Construct.objects.values(*columns)
    template_name = "constructs/construct_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        column_headers = [field.help_text for field in Construct._meta.get_fields() if field.name in self.columns]
        context['title'] = 'List of all constructs'
        context['headers'] = column_headers
        return context


class ConstructIndicatorValuesView(TemplateView):
    template_name = "constructs/construct_indicator_values.html"

    @register.filter
    def get_item(dictionary, key):
        return dictionary.get(key, '')

    def results(self):
        initialize_update_administration_data() # take this out later, make it a button maybe
        course_qs = Course.objects.exclude(format='site')
        result = self.construct.provide_indicator_results(course_qs, self.aggregation_type)
        return result

    def get_context_data(self, **kwargs):
        self.construct = get_object_or_404(Construct, id=self.kwargs.get("construct_id"))
        self.aggregation_type = self.kwargs.get("aggregation_type")
        context = super().get_context_data(**kwargs)
        context['title'] = f'Current {self.aggregation_type} indicator values of construct {self.construct.id} ({self.construct.name})'
        context['indicator_labels'] = list(self.construct.indicators.all().values_list('column_label', flat=True))
        return context


class ConstructCalculateListView(TemplateView):
    template_name = "constructs/construct_calculate.html"

    def results(self):
        course_qs = Course.objects.exclude(format='site')
        result = self.construct.calculate_result(course_qs)
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
        course_qs = Course.objects.exclude(format='site')
        self.construct.save_result(course_qs)  # take this out later, make it a button maybe
        queryset = ConstructResult.objects.filter(construct=self.construct).select_related('user')
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Database results of construct {self.construct.id} ({self.construct.name})'
        context['construct'] = self.construct
        return context