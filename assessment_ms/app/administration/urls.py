from django.urls import path

from .views import CourseListView, CourseStatusUpdateView, RoleAssignmentsListView, RoleAssignmentsStatusUpdateView

urlpatterns = [
    path('courses/', CourseListView.as_view()),
    path('courses/<int:course_id>/', CourseStatusUpdateView.as_view()),
    path('courses/<int:course_id>/roleassignments/', RoleAssignmentsListView.as_view()),
    path('courses/<int:course_id>/roleassignments/<int:roleassignment_id>/', RoleAssignmentsStatusUpdateView.as_view()),
]