from django.contrib import admin

from assessment.models.indicators import Indicator, IndicatorResult
from assessment.models.constructs import Construct, ConstructResult

admin.site.register(Indicator)
admin.site.register(IndicatorResult)

admin.site.register(Construct)
admin.site.register(ConstructResult)

