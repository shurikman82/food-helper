from rest_framework.authtoken import views
from django.urls import include, path

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
