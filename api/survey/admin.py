from django.contrib import admin

from .models import (
    ActorModel,
    AnswerActModel,
    QuestionModel,
    SurveyModel,
    ResponseOptionModel,
    SessionModel)

admin.site.register(SurveyModel)
admin.site.register(QuestionModel)
admin.site.register(ResponseOptionModel)
admin.site.register(AnswerActModel)
admin.site.register(ActorModel)
admin.site.register(SessionModel)
