from django.conf.urls import include
from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import *

router: DefaultRouter = DefaultRouter()

router.register(r"surveys", SurveyViewset)
router.register(r"questions", QuestionViewset)
router.register(r"responses", ResponseOptionViewset)
router.register(r"actors", ActorViewset)
router.register(r"sessions", SessionViewset)
router.register(r"answers", AnswerActViewset)

urlpatterns = [
    path("", include(router.urls)),
]
