from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('assessment/', include('assessment.urls')),
    path('administration/', include('administration.urls'))
]
