from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.db import connection

from .models import Course, User, RoleAssignments

from .forms import CourseStatusForm, RoleAssignmentsStatusForm


class CourseListView(ListView):
    template_name = "course_list.html"

    def get_queryset(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id as 'ID', fullname as 'Full name', shortname as 'Short name', \
                            DATE(startdate, 'unixepoch') as 'Start date', DATE(enddate, 'unixepoch') as 'End date', \
                            (case ignore_activity when False then 'On' else 'Off' end) as 'Status' \
                            FROM administration_course WHERE format <> 'site'")
            columns = [col[0] for col in cursor.description]
            dictfetchall = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return dictfetchall

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'List of all courses'
        return context


class CourseStatusUpdateView(FormView):
    template_name = 'course_status_update.html'
    form_class = CourseStatusForm
    success_url = '..'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        self.course = get_object_or_404(Course, id=self.kwargs.get("course_id"))
        self.course.ignore_activity = not self.course.ignore_activity
        form_kwargs['instance'] = self.course
        return form_kwargs

    def form_valid(self, form):
        course = form.save(commit=False)
        course.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if (self.course.ignore_activity):
            action = 'Disable'
        else:
            action = 'Enable'
        context['action'] = action
        context['title'] = f'{action} assessment for course'
        context['course'] = self.course
        return context


class RoleAssignmentsListView(ListView):
    template_name = "roleassignments_list.html"
    paginate_by = 20

    def get_queryset(self):
        self.course = get_object_or_404(Course, id=self.kwargs.get("course_id"))
        self.query_term = self.request.GET.get('user_search', None)
        with connection.cursor() as cursor:
            if self.query_term:
                cursor.execute("SELECT u.id as 'User ID', u.username as 'User name', ra.id as 'Assignment', \
                                r.shortname as 'Role', \
                                (case ra.ignore_activity when False then 'On' else 'Off' end) as 'Status' \
                            FROM administration_course c, administration_user u, \
                                administration_context cxt, administration_role r, administration_roleassignments ra \
                            WHERE ra.userid = u.id AND ra.contextid = cxt.id AND \
                                r.id = ra.roleid AND cxt.instanceid = c.id AND cxt.contextlevel = 50 AND \
                                c.id = %s AND u.id = %s\
                            ORDER BY [User ID]", [self.course.id, self.query_term])
            else:
                cursor.execute("SELECT u.id as 'User ID', u.username as 'User name', ra.id as 'Assignment', \
                                r.shortname as 'Role', \
                                (case ra.ignore_activity when False then 'On' else 'Off' end) as 'Status' \
                            FROM administration_course c, administration_user u, \
                                administration_context cxt, administration_role r, administration_roleassignments ra \
                            WHERE ra.userid = u.id AND ra.contextid = cxt.id AND \
                                r.id = ra.roleid AND cxt.instanceid = c.id AND cxt.contextlevel = 50 AND \
                                c.id = %s \
                            ORDER BY [User ID]", [self.course.id])
            columns = [col[0] for col in cursor.description]
            dictfetchall = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return dictfetchall

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'List of all users in course {self.course.id} ({self.course.fullname})'
        if self.query_term:
            context['query_term'] = self.query_term
        return context


class RoleAssignmentsStatusUpdateView(FormView):
    template_name = 'roleassignments_status_update.html'
    form_class = RoleAssignmentsStatusForm
    success_url = '..'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        self.course = get_object_or_404(Course, id=self.kwargs.get("course_id"))
        self.roleassignment = get_object_or_404(RoleAssignments, id=self.kwargs.get("roleassignment_id"))
        self.user = get_object_or_404(User, id=self.roleassignment.userid)
        self.roleassignment.ignore_activity = not self.roleassignment.ignore_activity
        form_kwargs['instance'] = self.roleassignment
        return form_kwargs

    def form_valid(self, form):
        roleassignment = form.save(commit=False)
        roleassignment.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if (self.roleassignment.ignore_activity):
            action = 'Disable'
        else:
            action = 'Enable'
        context['action'] = action
        context['title'] = f'{action} assessment for user in course'
        context['user'] = self.user
        context['course'] = self.course
        return context