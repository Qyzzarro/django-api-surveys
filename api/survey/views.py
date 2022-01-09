from django.http.response import HttpResponseBadRequest
from rest_framework import mixins
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.viewsets import GenericViewSet

from api.survey.utils.exceptions import EmptyQueryParamsException, WrongQueryParamsException
from api.survey.utils.permissions import (
    AllowListAndRetrieve, DontShowUnpublishedForNonStaff)
from api.survey.utils.viewsets import PermissedModelViewset
from api.survey.models import *
from api.survey.serializers import *


# ---------- SURVEY API ----------


class SurveyViewset(PermissedModelViewset):
    queryset = SurveyModel.objects.all()
    serializer_class = SurveyDetailSerializer
    permission_classes = [
        IsAdminUser | AllowListAndRetrieve, DontShowUnpublishedForNonStaff]


# ---------- QUESTION API ----------


class QuestionViewset(PermissedModelViewset):
    queryset = QuestionModel.objects.all()
    serializer_class = QuestionDetailSerializer
    permission_classes = [
        IsAdminUser | AllowListAndRetrieve, DontShowUnpublishedForNonStaff]


# ---------- RESPONSE OPTION API ----------


class ResponseOptionViewset(PermissedModelViewset):
    queryset = ResponseOptionModel.objects.all()
    serializer_class = ResponseOptionDetailSerializer
    permission_classes = [
        IsAdminUser | AllowListAndRetrieve, DontShowUnpublishedForNonStaff]


# ---------- ACTOR API ----------


class ActorViewset(GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    queryset = ActorModel.objects.all()
    serializer_class = ActorDetailSerializer
    permission_classes = [AllowAny]


# ---------- SESSION API ----------


class SessionViewset(GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    queryset = SessionModel.objects.all()
    serializer_class = SessionDetailSerializer
    permission_classes = [AllowAny]


# ---------- ANSWER ACT API ----------


class AnswerActViewset(
        GenericViewSet, mixins.ListModelMixin,
        mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    queryset = AnswerActModel.objects.all()
    serializer_class = AnswerActDetailSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except (WrongQueryParamsException, EmptyQueryParamsException) as e:
            return HttpResponseBadRequest(e)

    def get_queryset(self):
        queryset: QuerySet = super().get_queryset()

        if len(self.request.query_params) < 1:
            raise EmptyQueryParamsException("Here is no query params")

        for key in self.request.query_params.keys():
            if key == "actor":
                queryset = queryset.filter(
                    session__actor=self.request.query_params[key])
            elif key == "session":
                queryset = queryset.filter(
                    session=self.request.query_params[key])
            elif key == "question":
                queryset = queryset.filter(
                    response__question=self.request.query_params[key])
            else:
                raise WrongQueryParamsException("Request query param isn't accessible.")

        return queryset.order_by(("create_time"))
