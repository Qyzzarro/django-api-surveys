from django.conf.urls import include
from django.urls import path

from .views import (AuthView,)


urlpatterns = [
    path("auth/", AuthView.as_view()),
]
