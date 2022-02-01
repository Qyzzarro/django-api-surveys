from django.conf.urls import include
from django.urls import path

from .viewsets import (AuthView,)


urlpatterns = [
    path("auth/", AuthView.as_view({"post": "login", "get": "logout"})),
]
