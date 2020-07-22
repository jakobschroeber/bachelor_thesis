from django.contrib import admin
from django.urls import include, path

from pages.views import home_view, users_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view),
    path('data_sink/users/', users_view),
    path('assessment/', include('assessment.urls'))
]
