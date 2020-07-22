from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaulttags import register
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView

from .models_construct import Construct, ConstructResult
from .models_indicator import Indicator
from data_sink.models import MoodleUser
from .forms import ConstructForm



class ConstructCreateView(FormView):
    template_name = 'constructs/construct_detail.html'
    form_class = ConstructForm
    success_url = '..'

    def form_valid(self, form):
        Construct.objects.create(**form.cleaned_data)
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
        construct = form.save(commit=False)
        construct.save()
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
        userid_list = list(MoodleUser.objects.filter(ignore_activity=False).values_list('id', flat=True))
        value_options = { # maybe additional construct attribute or foreign key of a value type model
            'standardized':    self.construct.provide_standardized_indicator_results(userid_list),
            'normalized':      self.construct.provide_normalized_indicator_results(userid_list),
            'original':        self.construct.provide_indicator_results(userid_list)
        }
        result = value_options.get(self.value_type) # key error in case of not-existing value_type
        return result

    def get_context_data(self, **kwargs):
        self.construct = get_object_or_404(Construct, id=self.kwargs.get("construct_id"))
        self.value_type = self.kwargs.get("value_type")
        context = super().get_context_data(**kwargs)
        context['title'] = f'Current {self.value_type} indicator values of construct {self.construct.id} ({self.construct.name})'
        context['indicator_labels'] = list(self.construct.indicator_set.all().values_list('column_label', flat=True))
        return context


class ConstructCalculateListView(TemplateView):
    template_name = "constructs/construct_calculate.html"

    def results(self):
        userid_list = list(MoodleUser.objects.filter(ignore_activity=False).values_list('id', flat=True))
        result = self.construct.calculate_result(userid_list)
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
        self.construct.save_result(MoodleUser.objects.all())  # take this out later, make it a parameter maybe
        queryset = ConstructResult.objects.filter(construct=self.construct).select_related('user')
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Database results of construct {self.construct.id} ({self.construct.name})'
        context['construct'] = self.construct
        return context