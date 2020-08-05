from django.urls import path

from .views import CourseListView, RoleAssignmentsListView, RoleAssignmentsUpdateView

urlpatterns = [
    path('courses/', CourseListView.as_view()),
    path('courses/<int:course_id>/roleassignments/', RoleAssignmentsListView.as_view()),
    path('courses/<int:course_id>/roleassignments/<int:roleassignment_id>/', RoleAssignmentsUpdateView.as_view()),
]