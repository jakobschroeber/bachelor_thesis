from django.contrib import admin

from .models_source import SourceMoodleUser, SourceMoodleUserPreferences, SourceMoodleLogstoreStandardLog, \
    SourceMoodleAssign, SourceMoodleAssignSubmission, SourceMoodleComments, SourceMoodleCourseModules, \
    SourceMoodleTagInstance

admin.site.register(SourceMoodleUser)
admin.site.register(SourceMoodleUserPreferences)
admin.site.register(SourceMoodleLogstoreStandardLog)
admin.site.register(SourceMoodleAssign)
admin.site.register(SourceMoodleAssignSubmission)
admin.site.register(SourceMoodleComments)
admin.site.register(SourceMoodleCourseModules)
admin.site.register(SourceMoodleTagInstance)

