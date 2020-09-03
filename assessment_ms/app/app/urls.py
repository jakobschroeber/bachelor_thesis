from django.contrib import admin
from django.urls import include, path
from export.views import ConstructResultsAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('assessment/', include('assessment.urls')),
    path('administration/', include('administration.urls')),
    path('api/', ConstructResultsAPIView.as_view())
]
