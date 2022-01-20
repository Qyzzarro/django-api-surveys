from typing import List

from rest_framework import serializers

from .models import (
    ActorModel,
    AnswerActModel,
    QuestionModel,
    ResponseOptionModel,
    SessionModel,
    SurveyModel, )
from .utils.relations import ModelRelaitedField


class QuestionShortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = QuestionModel
        fields = ["pk", "url", "type", "content", ]


class ResponseOptionShortSerializer(serializers.HyperlinkedModelSerializer):
    question = ModelRelaitedField(
        serializer_class=QuestionShortSerializer, queryset=QuestionModel.objects.all())

    class Meta:
        model = ResponseOptionModel
        fields = ["pk", "url", "question", "content", ]


class ResponseOptionDetailSerializer(serializers.HyperlinkedModelSerializer):
    question = ModelRelaitedField(
        serializer_class=QuestionShortSerializer, queryset=QuestionModel.objects.all())

    class Meta:
        model = ResponseOptionModel
        fields = ["pk", "url", "question", "content", "is_published", ]


class QuestionDetailSerializer(serializers.HyperlinkedModelSerializer):
    response_options = ResponseOptionShortSerializer(many=True, required=False)

    class Meta:
        model = QuestionModel
        fields = ["pk", "url", "survey", "type", "content",
                  "response_options", "is_published", ]


class SurveyShortSerializer(serializers.HyperlinkedModelSerializer):
    questions = QuestionShortSerializer(many=True, required=False)

    class Meta:
        model = SurveyModel
        fields = ["pk", "header", "description", "questions", ]


class SurveyDetailSerializer(serializers.HyperlinkedModelSerializer):
    questions = QuestionShortSerializer(many=True, required=False)
    is_published = serializers.ReadOnlyField(read_only=True)

    class Meta:
        model = SurveyModel
        fields = ["pk", "url", "header", "description", "questions",
                  "begin_date", "end_date", "is_published", ]


class ActorShortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ActorModel
        fields = ["pk", "url", ]


class SessionShortSerializer(serializers.HyperlinkedModelSerializer):
    actor = ModelRelaitedField(
        serializer_class=ActorShortSerializer,
        queryset=ActorModel.objects.all())

    class Meta:
        model = SessionModel
        fields = ["pk", "url", "actor"]


class SessionDetailSerializer(serializers.HyperlinkedModelSerializer):
    actor = ModelRelaitedField(
        queryset=ActorModel.objects.all(),
        serializer_class=ActorShortSerializer)

    answer_acts = ActorShortSerializer(many=True, required=False)

    class Meta:
        model = SessionModel
        fields = ["pk", "url", "actor", "answer_acts"]


class ActorDetailSerializer(serializers.HyperlinkedModelSerializer):
    sessions = SessionShortSerializer(many=True, required=False)

    class Meta:
        model = ActorModel
        fields = ["pk", "url", "sessions", ]


class AnswerActDetailSerializer(serializers.HyperlinkedModelSerializer):
    session = ModelRelaitedField(
        queryset=SessionModel.objects.all(),
        serializer_class=SessionShortSerializer)

    response = ModelRelaitedField(
        queryset=ResponseOptionModel.objects.all(),
        serializer_class=ResponseOptionShortSerializer)

    class Meta:
        model = AnswerActModel
        fields = ["pk", "url", "session", "response", ]
