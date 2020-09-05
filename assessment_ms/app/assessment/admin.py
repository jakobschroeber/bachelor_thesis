from django.contrib import admin

from assessment.models.indicators import Indicator, IndicatorResult
from assessment.models.constructs import Construct, ConstructIndicatorRelation, ConstructAssessment, ConstructResult,\
    ConstructIndicatorResult

admin.site.register(Indicator)
admin.site.register(IndicatorResult)

admin.site.register(Construct)
admin.site.register(ConstructIndicatorRelation)

admin.site.register(ConstructAssessment)
admin.site.register(ConstructResult)
admin.site.register(ConstructIndicatorResult)