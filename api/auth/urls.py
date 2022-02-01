from django.conf.urls import include
from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import *


urlpatterns = [
    path("auth/", AuthView.as_view()),
]
