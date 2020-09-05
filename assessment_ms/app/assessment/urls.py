from django.urls import path

from assessment.views.indicators import IndicatorListView, IndicatorCreateView, IndicatorDeleteView, IndicatorUpdateView, \
    IndicatorCalculateListView, IndicatorResultsListView, IndicatorScheduleUpdateView, IndicatorStatusUpdateView

from assessment.views.constructs import ConstructListView, ConstructCreateView, ConstructDeleteView, ConstructUpdateView, \
    ConstructCalculateListView, ConstructIndicatorWeightUpdateView, ConstructIndicatorValuesView, ConstructResultsListView, \
    ConstructScheduleUpdateView, ConstructStatusUpdateView


urlpatterns = [
    path('indicators/', IndicatorListView.as_view()),
    path('indicators/create/', IndicatorCreateView.as_view()),
    path('indicators/<int:indicator_id>/delete/', IndicatorDeleteView.as_view()),
    path('indicators/<int:indicator_id>/indicator-update/', IndicatorUpdateView.as_view()),
    path('indicators/<int:indicator_id>/schedule-update/', IndicatorScheduleUpdateView.as_view()),
    path('indicators/<int:indicator_id>/status-update/', IndicatorStatusUpdateView.as_view()),
    path('indicators/<int:indicator_id>/calculate/', IndicatorCalculateListView.as_view()),
    path('indicators/<int:indicator_id>/results/', IndicatorResultsListView.as_view()),
    path('constructs/', ConstructListView.as_view()),
    path('constructs/create/', ConstructCreateView.as_view()),
    path('constructs/<int:construct_id>/delete/', ConstructDeleteView.as_view()),
    path('constructs/<int:construct_id>/construct-update/', ConstructUpdateView.as_view()),
    path('constructs/<int:construct_id>/schedule-update/', ConstructScheduleUpdateView.as_view()),
    path('constructs/<int:construct_id>/status-update/', ConstructStatusUpdateView.as_view()),
    path('constructs/<int:construct_id>/indicators/', IndicatorListView.as_view()),
    path('constructs/<int:construct_id>/indicators/indicator_weights/', ConstructIndicatorWeightUpdateView.as_view()),
    path('constructs/<int:construct_id>/indicators/create/', IndicatorCreateView.as_view()),
    path('constructs/<int:construct_id>/indicators/<int:indicator_id>/', IndicatorUpdateView.as_view()),
    path('constructs/<int:construct_id>/indicators/<int:indicator_id>/delete/', IndicatorDeleteView.as_view()),
    path('constructs/<int:construct_id>/indicators/<int:indicator_id>/calculate/', IndicatorCalculateListView.as_view()),
    path('constructs/<int:construct_id>/indicators/<int:indicator_id>/results/', IndicatorResultsListView.as_view()),
    path('constructs/<int:construct_id>/indicator_values/', ConstructIndicatorValuesView.as_view()),
    path('constructs/<int:construct_id>/calculate/', ConstructCalculateListView.as_view()),
    path('constructs/<int:construct_id>/results/', ConstructResultsListView.as_view()),
]