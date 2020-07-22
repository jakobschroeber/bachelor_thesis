# from django.contrib import admin
from django.urls import path

from .views_indicator import IndicatorListView, IndicatorCreateView, IndicatorUpdateView, IndicatorCalculateListView, \
    IndicatorResultsListView

from .views_construct import ConstructListView, ConstructCreateView, ConstructUpdateView, ConstructCalculateListView, \
    ConstructIndicatorValuesView, ConstructResultsListView


urlpatterns = [
    path('indicators/', IndicatorListView.as_view()),
    path('indicators/create/', IndicatorCreateView.as_view()),
    path('indicators/<int:indicator_id>/', IndicatorUpdateView.as_view()),
    path('indicators/<int:indicator_id>/calculate/', IndicatorCalculateListView.as_view()),
    path('indicators/<int:indicator_id>/results/', IndicatorResultsListView.as_view()),
    path('constructs/', ConstructListView.as_view()),
    path('constructs/create/', ConstructCreateView.as_view()),
    path('constructs/<int:construct_id>/', ConstructUpdateView.as_view()),
    path('constructs/<int:construct_id>/indicators/', IndicatorListView.as_view()),
    path('constructs/<int:construct_id>/indicators/create/', IndicatorCreateView.as_view()),
    path('constructs/<int:construct_id>/indicators/<int:indicator_id>/', IndicatorUpdateView.as_view()),
    path('constructs/<int:construct_id>/indicators/<int:indicator_id>/calculate/', IndicatorCalculateListView.as_view()),
    path('constructs/<int:construct_id>/indicators/<int:indicator_id>/results/', IndicatorResultsListView.as_view()),
    path('constructs/<int:construct_id>/indicator_values/<str:value_type>/', ConstructIndicatorValuesView.as_view()),
    path('constructs/<int:construct_id>/calculate/', ConstructCalculateListView.as_view()),
    path('constructs/<int:construct_id>/results/', ConstructResultsListView.as_view()),
]