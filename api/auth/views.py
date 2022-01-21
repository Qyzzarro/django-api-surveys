import json

from django.http import (
    HttpResponse,
    HttpRequest,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseForbidden,
)
from django.contrib.auth import (authenticate, login, logout,)

from rest_framework.views import (View,)


class Login(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            data = json.loads(request.body.replace(b"'", b'"'))
        except json.JSONDecodeError as e:
            return HttpResponseBadRequest(f"{request.body} isn't JSON.")

        username = data.get('username')
        password = data.get('password')
        if username is None or password is None:
            return HttpResponseBadRequest('Please provide username and password.')
        user = authenticate(username=username, password=password)
        if user is None:
            return HttpResponseForbidden('Invalid credentials.')
        login(request, user)
        return HttpResponse('Successfully logged in.')


class Logout(View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponseNotAllowed('You\'re not logged in.')

        logout(request)
        return HttpResponse('Successfully logged out.')
