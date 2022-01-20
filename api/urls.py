
from django.contrib import admin
from django.urls import path
from django.urls.conf import include


urlpatterns = [
    path('api/', include('api.survey.urls')),
    path('auth/', include('api.auth.urls')),
]
