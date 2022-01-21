
from django.contrib import admin
from django.urls import path
from django.urls.conf import include


urlpatterns = [
    path('v1/', include('api.survey.urls')),
    path('v1/', include('api.auth.urls')),
]
