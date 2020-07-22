from django.contrib import admin

from .models_indicator import Indicator, IndicatorResult
from .models_construct import Construct, ConstructResult

admin.site.register(Indicator)
admin.site.register(IndicatorResult)

admin.site.register(Construct)
admin.site.register(ConstructResult)

