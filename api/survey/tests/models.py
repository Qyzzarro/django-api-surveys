from datetime import timedelta
from datetime import date
from uuid import uuid4

from django.test import TestCase

from .models import *
from .utils import *


class SurveyModelTestCase(TestCase):
    def test_end_date_and_publication_status(self):
        for deltaday in range(-1, 2, 1):
            survey = create_test_survey_via_model(
                end_date=date.today() + timedelta(days=deltaday))
            self.assertEqual(
                survey.is_published,
                survey.end_date >= date.today())

    def test_begin_date_and_publication_status(self):
        for deltaday in range(-1, 2, 1):
            survey = create_test_survey_via_model(
                begin_date=date.today() + timedelta(days=deltaday))
            self.assertEqual(
                survey.is_published,
                survey.begin_date <= date.today())

    def test_begin_end_date_range_and_publication_status(self):
        for begin_deltaday in range(-1, 2, 1):
            for end_deltaday in range(begin_deltaday, 2, 1):
                survey = create_test_survey_via_model(
                    begin_date=date.today() + timedelta(days=begin_deltaday),
                    end_date=date.today() + timedelta(days=end_deltaday))
                self.assertEqual(
                    survey.is_published,
                    survey.begin_date <= date.today() and survey.end_date >= date.today())

    def test_block_begin_date(self):
        survey = create_test_survey_via_model(begin_date=date.today())
        survey.begin_date += timedelta(days=1)
        survey.save()
        self.assertEqual(
            survey.begin_date,
            date.today())


class QuestionModelTestCase(TestCase):
    def test_create_fake_resposen_option(self):
        survey = create_test_survey_via_model()
        question = create_test_questions_via_model(survey, ("text",), 1)[0]

        self.assertEqual(
            ResponseOptionModel.objects.filter(question=question).count(), 1)
        for response_option in question.get_response_options():
            self.assertEqual(response_option.content, "fake_answer")

    def test_have_fake_answer(self):
        survey = create_test_survey_via_model()
        question = create_test_questions_via_model(survey, ("text",), 1)[0]

        self.assertEqual(
            question.have_fake_answer,
            bool(ResponseOptionModel.objects.get(question=question)))


class ResponseOptionModelTestCase(TestCase):
    def test_create_fake_answer_for_text_question(self):
        survey = create_test_survey_via_model()
        question = create_test_questions_via_model(survey, ("text",), 1)[0]

        self.assertEqual(
            ResponseOptionModel.objects.filter(question=question).count(),
            1)

    def test_creation_of_text_response_option(self):
        survey = create_test_survey_via_model()
        question = create_test_questions_via_model(survey, ("text",), 1)[0]

        try:
            create_test_response_options_via_model(question, 1)
        except BaseException as e:
            self.assertIsInstance(e, NumberExcess)

        self.assertEqual(
            ResponseOptionModel.objects.filter(
                question=question).count(),
            1,
            "Number of response option for test question was exceeded.")


class ActorModelTestCase(TestCase):
    def test_block_actor_unique_key(self):
        actor = create_test_actors_via_model(1)[0]

        first_unique_key = actor.unique_key

        actor.unique_key = uuid.uuid4()
        actor.save()

        self.assertEqual(
            first_unique_key,
            actor.unique_key)

    def test_have_actors_unique_key(self):
        actors = create_test_actors_via_model(5)
        actor_keys: List[uuid4] = [str(actor.unique_key) for actor in actors]
        self.assertEqual(
            len(set(actor_keys)), len(actor_keys))


class SessionModelTestCase(TestCase):
    def test_block_session_unique_key(self):
        actor = create_test_actors_via_model(1)[0]
        session = create_test_sessions_via_model(actor, 1)[0]

        unique_key = session.unique_key

        session.unique_key = uuid.uuid4()
        session.save()

        self.assertEqual(
            unique_key,
            session.unique_key)

    def test_have_sessions_unique_key(self):
        actor = create_test_actors_via_model(1)[0]
        sessions = create_test_sessions_via_model(actor, 5)
        session_keys: List[uuid4] = [
            session.unique_key for session in sessions]
        self.assertEqual(
            len(set(session_keys)), len(session_keys))


class AnswerActTestCase(TestCase):
    def test_one_answer_question_in_single_session(self):
        survey = create_test_survey_via_model()
        questions = create_test_questions_via_model(survey, ("one",), 3)
        response_options: List[ResponseOptionModel] = []
        for question in questions:
            response_options.extend(
                create_test_response_options_via_model(question, 3))

        actor = create_test_actors_via_model(1)[0]
        session = create_test_sessions_via_model(actor, 1)[0]

        for question in questions:
            try:
                for response in question.get_response_options():
                    answer_act = create_test_answer_act_via_model(
                        session, response)
            except BaseException as e:
                self.assertIsInstance(e, NumberExcess)
                self.assertEqual(
                    AnswerActModel.objects.filter(
                        session=session,
                        response__question=question).count(),
                    1)
            else:
                self.fail()

    def test_one_answer_question_in_different_sessions(self):
        survey = create_test_survey_via_model()
        questions = create_test_questions_via_model(survey, ("one",), 3)
        response_options: List[ResponseOptionModel] = []
        for question in questions:
            response_options.extend(
                create_test_response_options_via_model(question, 3))

        actor = create_test_actors_via_model(1)[0]
        sessions = create_test_sessions_via_model(actor, 3)

        for session in sessions:
            for question in questions:
                try:
                    for response_option in question.get_response_options():
                        answer_act = create_test_answer_act_via_model(
                            session, response_option)
                except BaseException as e:
                    self.assertIsInstance(e, NumberExcess)
                else:
                    self.fail()

                self.assertEqual(
                    AnswerActModel.objects.filter(
                        session=session,
                        response__question=question).count(),
                    1)

        self.assertEqual(
            AnswerActModel.objects.filter(
                session=session,
                response__question=question).count(),
            1)

    def test_many_answers_question_in_single_session(self):
        survey = create_test_survey_via_model()
        questions = create_test_questions_via_model(survey, ("many",), 3)
        responses: List[ResponseOptionModel] = []
        for question in questions:
            responses.extend(
                create_test_response_options_via_model(question, 3))

        actor = create_test_actors_via_model(1)[0]
        session = create_test_sessions_via_model(actor, 1)[0]

        for question in questions:
            for response_option in question.get_response_options():
                try:
                    for _ in range(3):
                        answer_act = create_test_answer_act_via_model(
                            session, response_option)
                except BaseException as e:
                    self.assertIsInstance(e, NumberExcess)
                else:
                    self.fail()

            self.assertEqual(
                AnswerActModel.objects.filter(
                    response__question=question).count(),
                ResponseOptionModel.objects.filter(question=question).count())

        # self.assertEqual(
        #     AnswerActModel.objects.count(),
        #     ResponseOptionModel.objects.count())

    def test_many_answers_question_in_different_session(self):
        survey = create_test_survey_via_model()
        questions = create_test_questions_via_model(survey, ("many",), 3)
        responses: List[ResponseOptionModel] = []
        for question in questions:
            responses.extend(
                create_test_response_options_via_model(question, 3))

        actor = create_test_actors_via_model(1)[0]
        sessions = create_test_sessions_via_model(actor, 3)

        for session in sessions:
            for question in questions:
                for response_option in question.get_response_options():
                    try:
                        for _ in range(3):
                            answer_act = create_test_answer_act_via_model(
                                session, response_option)
                    except BaseException as e:
                        self.assertIsInstance(e, NumberExcess)
                    else:
                        self.fail()

                self.assertEqual(
                    AnswerActModel.objects.filter(
                        response__question=question,
                        session=session).count(),
                    ResponseOptionModel.objects.filter(question=question).count())

        # self.assertEqual(
        #     AnswerActModel.objects.count(),
        #     ResponseOptionModel.objects.count() * len(sessions))

    def test_text_answer_question_in_single_session(self):
        survey = create_test_survey_via_model()
        questions = create_test_questions_via_model(survey, ("text",), 3)

        actor = create_test_actors_via_model(1)[0]
        session = create_test_sessions_via_model(actor, 1)[0]

        for question in questions:
            for response_option in question.get_response_options():
                try:
                    for _ in range(3):
                        answer_act = create_test_answer_act_via_model(
                            session, response_option)
                except BaseException as e:
                    self.assertIsInstance(e, NumberExcess)
                else:
                    self.fail()

            self.assertEqual(
                AnswerActModel.objects.filter(
                    session=session,
                    response__question=question).count(),
                1)

    def test_text_answer_question_in_different_sessions(self):
        survey = create_test_survey_via_model()
        questions = create_test_questions_via_model(survey, ("text",), 3)

        actor = create_test_actors_via_model(1)[0]
        sessions = create_test_sessions_via_model(actor, 3)

        for session in sessions:
            for question in questions:
                for response_option in question.get_response_options():
                    try:
                        for _ in range(3):
                            answer_act = create_test_answer_act_via_model(
                                session, response_option)
                    except BaseException as e:
                        self.assertIsInstance(e, NumberExcess)
                    else:
                        self.fail(e)

            self.assertEqual(
                AnswerActModel.objects.filter(
                    response__question=question,
                    session=session
                ).count(),
                ResponseOptionModel.objects.filter(question=question).count())
