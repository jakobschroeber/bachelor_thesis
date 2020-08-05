from django.contrib import admin

from .models import User, Course, Context, Role, \
    RoleAssignments

admin.site.register(User)
admin.site.register(Course)
admin.site.register(Context)
admin.site.register(Role)
admin.site.register(RoleAssignments)

