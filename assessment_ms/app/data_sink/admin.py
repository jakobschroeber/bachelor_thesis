from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import MoodleUser #, MoodleLogstoreStandardLog

admin.site.register(MoodleUser, SimpleHistoryAdmin)
# admin.site.register(MoodleLogstoreStandardLog)