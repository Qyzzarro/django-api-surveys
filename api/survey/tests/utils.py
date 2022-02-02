from typing import Iterable, List
from datetime import date, timedelta

from django.contrib.auth import models
from django.test.client import Client

from ..models import *


def create_test_actors_via_model(count: int, user: models.User = None) -> List[ActorModel]:
    actors: List[ActorModel] = []
    for _ in range(count):
        actor = ActorModel(user=user)
        actor.save()
        actors.append(actor)
    return actors


def create_test_answer_act_via_model(session: SessionModel, response_option: ResponseOptionModel) \
        -> AnswerActModel:
    answer_act = AnswerActModel(
        session=session, response=response_option)
    answer_act.save()
    return answer_act


def create_test_response_options_via_model(question: QuestionModel, number: int) -> List[ResponseOptionModel]:
    response_options: List[ResponseOptionModel] = []
    for i in range(number):
        response_option = ResponseOptionModel(
            question=question,
            content=f"Answer #{i} for question (type:{question.type})")
        response_option.save()
        response_options.append(response_option)
    return response_options


def create_test_sessions_via_model(actor: ActorModel, number_per_actor: int) -> List[SessionModel]:
    sessions: List[SessionModel] = []

    for _ in range(number_per_actor):
        session = SessionModel(actor=actor)
        session.save()
        sessions.append(session)

    return sessions


def create_test_survey_via_model(begin_date: date | None = None, end_date: date | None = None):
    survey = SurveyModel(
        header="Test survey",
        description=f"Test survey [{begin_date}, {end_date}]",
        begin_date=begin_date,
        end_date=end_date)
    survey.save()
    return survey


def create_test_surveys_via_model() -> List[SurveyModel]:
    surveys: List[SurveyModel] = []

    for first_day in range(-1, 2, 1):
        for last_day in range(first_day, first_day + 2, 1):
            survey = create_test_survey_via_model(
                begin_date=date.today() + timedelta(days=first_day),
                end_date=date.today() + timedelta(days=last_day))
            surveys.append(survey)

        survey = create_test_survey_via_model(
            begin_date=date.today() + timedelta(days=first_day))
        surveys.append(survey)

        survey = create_test_survey_via_model(
            end_date=date.today() + timedelta(days=first_day))
        surveys.append(survey)

    return surveys


def create_test_questions_via_model(
    survey: SurveyModel, types: Iterable[str], number: int) \
        -> List[QuestionModel]:
    questions: List[QuestionModel] = []

    for type in types:
        for _ in range(number):
            question = QuestionModel(
                survey=survey,
                type=type,
                content=f"Test question (type:{type}, survey:{survey})")
            question.save()
            questions.append(question)

    return questions


def create_test_answer_acts_via_model(sessions: Iterable[SessionModel], responses: Iterable[ResponseOptionModel]) \
        -> List[AnswerActModel]:
    question_for_skip: List[QuestionModel] = []
    answer_acts: List[AnswerActModel] = []
    for response in responses:
        if response.question in question_for_skip:
            continue

        for session in sessions:
            answer_act = AnswerActModel(session=session, response=response)
            answer_act.save()
            answer_acts.append(answer_act)

        if response.type in ["one", "text"]:
            question_for_skip.append(response.question)

    return answer_acts


def create_test_surveys_questions_and_response_options_via_model(number_of_questions: int = 3, number_of_responses: int = 3):
    surveys = create_test_surveys_via_model()

    questions: List[QuestionModel] = []
    for survey in surveys:
            questions.extend(create_test_questions_via_model(
                survey, ("one", "many", "text"), number_of_questions))

    responses: List[ResponseOptionModel] = []
    for question in questions:
        if question.type != "text":
            responses.extend(
                create_test_response_options_via_model(question, number_of_responses))

    # n_Q = {
    #     "text": Question.objects.filter(type="text").count(),
    #     "many": Question.objects.filter(type="many").count(),
    #     "one": Question.objects.filter(type="one").count(),
    # }

    # n_R = {
    #     "text": ResponseOption.objects.filter(question__type="text").count(),
    #     "many": ResponseOption.objects.filter(question__type="many").count(),
    #     "one": ResponseOption.objects.filter(question__type="one").count(),
    # }

    return surveys, questions, responses


def create_test_admin(username="admin", password="admin"):
    admin = models.User(username=username)
    admin.set_password(password)
    admin.is_staff, admin.is_superuser = True, True
    admin.save()
    return admin


def create_test_user(username="user", password="user"):
    user = models.User(username=username)
    user.set_password(password)
    user.save()
    return user


def create_test_question_via_http(client: Client, survey_url: str, type: str):
    return client.post(path="/api/v1/questions/", data={
        "survey": survey_url,
        "type": type,
        "content": f"Test question (type:{type})",
    })

def create_test_actors_sessions_and_answers_via_api(user: models.User = None):
    actors = create_test_actors_via_model(1, user)
    sessions: List[SessionModel] = []
    for actor in actors:
        sessions.extend(create_test_sessions_via_model(actor, 1))
    answers = create_test_answer_acts_via_model(
        sessions, ResponseOptionModel.objects.all())
    return actors, sessions, answers