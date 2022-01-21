from datetime import date, datetime

from django.test.testcases import TestCase

from .utils import *


class SurveyViewsetTestCase(TestCase):
    def test_list_surveys_by_anon(self):
        create_test_surveys_questions_and_response_options_via_model()
        page_url = "/api/v1/surveys/"
        while page_url:
            response = self.client.get(path=page_url)
            self.assertEqual(response.status_code, 200, response.data)
            for result in response.data["results"]:
                self.assertTrue(result["is_published"])
                if result["begin_date"] != None:
                    self.assertLessEqual(
                        datetime.strptime(
                            result["begin_date"], "%Y-%m-%d").date(),
                        date.today())
                if result["end_date"] != None:
                    self.assertLessEqual(
                        date.today(),
                        datetime.strptime(result["end_date"], "%Y-%m-%d").date())
            page_url = response.data["next"]

    def test_list_surveys_staff(self):
        create_test_surveys_questions_and_response_options_via_model()
        create_test_admin()
        self.assertTrue(
            self.client.login(username="admin", password="admin"))
        page_url = "/api/v1/surveys/"
        while page_url:
            response = self.client.get(path=page_url)
            self.assertEqual(response.status_code, 200, response.data)
            for result in response.data["results"]:
                today_in_begin_end_range: bool = True
                if result["begin_date"] != None:
                    begin_date = datetime.strptime(
                        result["begin_date"], "%Y-%m-%d").date()
                    today_in_begin_end_range &= begin_date <= date.today()
                if result["end_date"] != None:
                    end_date = datetime.strptime(
                        result["end_date"], "%Y-%m-%d").date()
                    today_in_begin_end_range &= date.today() <= end_date
                self.assertEqual(today_in_begin_end_range,
                                 result["is_published"])
            page_url = response.data["next"]

    def test_retrieve_survey_anon(self):
        create_test_surveys_questions_and_response_options_via_model()
        for db_survey in SurveyModel.objects.all():
            response = self.client.get(path=f"/api/v1/surveys/{db_survey.pk}/")
            if db_survey.is_published:
                self.assertEqual(response.status_code, 200, response.data)
                self.assertTrue(response.data["is_published"])
                if response.data["begin_date"] != None:
                    self.assertLessEqual(
                        datetime.strptime(
                            response.data["begin_date"], "%Y-%m-%d").date(),
                        date.today())
                if response.data["end_date"] != None:
                    self.assertLessEqual(
                        date.today(),
                        datetime.strptime(
                            response.data["end_date"], "%Y-%m-%d").date())
                self.assertEqual(
                    len(response.data["questions"]),
                    QuestionModel.objects.filter(survey=db_survey.pk).count())
            else:
                self.assertEqual(response.status_code, 403)

    def test_retrieve_survey_staff(self):
        create_test_surveys_questions_and_response_options_via_model()
        create_test_admin()
        self.assertTrue(
            self.client.login(username="admin", password="admin"))
        for db_survey in SurveyModel.objects.all():
            response = self.client.get(path=f"/api/v1/surveys/{db_survey.pk}/")
            self.assertEqual(response.status_code, 200, response.data)
            self.assertEqual(
                response.data["is_published"],
                db_survey.is_published)
            self.assertEqual(
                len(response.data["questions"]),
                QuestionModel.objects.filter(survey=db_survey.pk).count())

    def test_post_surveys_staff(self):
        create_test_admin()
        self.assertTrue(
            self.client.login(username="admin", password="admin"))
        for begin_deltaday in range(-1, 2, 1):
            for end_deltaday in range(begin_deltaday, begin_deltaday + 2, 1):
                response = self.client.post(path="/api/v1/surveys/", data={
                    "header": "Test survey header",
                    "description": "test survey desctiprion",
                    "begin_date": str(date.today() + timedelta(days=begin_deltaday)),
                    "end_date": str(date.today() + timedelta(days=end_deltaday)), })
                self.assertEqual(
                    response.status_code,
                    201, response.data)

        for end_deltaday in range(-1, 2, 1):
            response = self.client.post(path="/api/v1/surveys/", data={
                "header": "Test survey header",
                "description": "test survey desctiprion",
                "end_date": str(date.today() + timedelta(days=end_deltaday)), })
            self.assertEqual(
                response.status_code,
                201, response.data)

        for begin_deltaday in range(-1, 2, 1):
            response = self.client.post(path="/api/v1/surveys/", data={
                "header": "Test survey header",
                "description": "test survey desctiprion",
                "begin_date": str(date.today() + timedelta(days=begin_deltaday)), })
            self.assertEqual(
                response.status_code,
                201, response.data)

    def test_post_surveys_staff(self):
        for begin_deltaday in range(-1, 2, 1):
            for end_deltaday in range(begin_deltaday, begin_deltaday + 2, 1):
                response = self.client.post(path="/api/v1/surveys/", data={
                    "header": "Test survey header",
                    "description": "test survey desctiprion",
                    "begin_date": str(date.today() + timedelta(days=begin_deltaday)),
                    "end_date": str(date.today() + timedelta(days=end_deltaday)), })
                self.assertEqual(
                    response.status_code,
                    403, response.data)

        for end_deltaday in range(-1, 2, 1):
            response = self.client.post(path="/api/v1/surveys/", data={
                "header": "Test survey header",
                "description": "test survey desctiprion",
                "end_date": str(date.today() + timedelta(days=end_deltaday)), })
            self.assertEqual(
                response.status_code,
                403, response.data)

        for begin_deltaday in range(-1, 2, 1):
            response = self.client.post(path="/api/v1/surveys/", data={
                "header": "Test survey header",
                "description": "test survey desctiprion",
                "begin_date": str(date.today() + timedelta(days=begin_deltaday)), })
            self.assertEqual(
                response.status_code,
                403, response.data)


class QuestionViewsetTestCase(TestCase):
    def test_list_questions_anon(self):
        create_test_surveys_questions_and_response_options_via_model()
        page_url = "/api/v1/questions/"
        while page_url:
            response = self.client.get(path=page_url)
            self.assertEqual(response.status_code, 200, response.data)
            for question in response.data["results"]:
                self.assertTrue(question["is_published"])
                self.assertEqual(
                    len(question["response_options"]),
                    ResponseOptionModel.objects.filter(
                        question=question["pk"]).count())
            page_url = response.data["next"]

    def test_get_questions_anon(self):
        create_test_surveys_questions_and_response_options_via_model()
        for db_question in QuestionModel.objects.all():
            response = self.client.get(
                path=f"/api/v1/questions/{db_question.pk}/")

            if db_question.is_published:
                self.assertEqual(response.status_code, 200, response.data)
                self.assertTrue(response.data["is_published"])
                self.assertEqual(
                    len(response.data["response_options"]),
                    ResponseOptionModel.objects.filter(
                        question=db_question.pk).count())
            else:
                self.assertEqual(response.status_code, 403)

    def test_list_questions_staff(self):
        create_test_surveys_questions_and_response_options_via_model()
        create_test_admin()
        self.assertTrue(
            self.client.login(username="admin", password="admin"))
        getted_question_pks_via_api = []

        page_url = "/api/v1/questions/"
        while page_url:
            response = self.client.get(path=page_url)
            self.assertEqual(response.status_code, 200, response.data)
            for question in response.data["results"]:
                self.assertEqual(
                    len(question["response_options"]),
                    ResponseOptionModel.objects.filter(
                        question=question["pk"]).count())
                self.assertFalse(
                    question["pk"] in getted_question_pks_via_api,
                    "Here is found questions that is duplicated in API. idk")
                getted_question_pks_via_api.append(question["pk"])
            page_url = response.data["next"]

        for question in QuestionModel.objects.all():
            self.assertTrue(
                question.pk in getted_question_pks_via_api,
                "Here is found questions that is not represented in API.")

    def test_get_question_staff(self):
        create_test_surveys_questions_and_response_options_via_model()
        create_test_admin()
        self.assertTrue(
            self.client.login(username="admin", password="admin"))

        for db_question in QuestionModel.objects.all():
            response = self.client.get(
                path=f"/api/v1/questions/{db_question.pk}/")
            self.assertEqual(response.status_code, 200, response.data)
            self.assertEqual(
                len(response.data["response_options"]),
                ResponseOptionModel.objects.filter(
                    question=db_question.pk
                ).count())

    def test_post_questions_staff(self):
        surveys = create_test_surveys_via_model()
        create_test_admin()
        self.assertTrue(
            self.client.login(username="admin", password="admin"))

        page_url = "/api/v1/surveys/"
        while page_url:
            response_from_surveys = self.client.get(path=page_url)
            self.assertEqual(
                response_from_surveys.status_code,
                200,
                response_from_surveys.data)

            for survey in response_from_surveys.data["results"]:
                for question_type in ["one", "many", "text"]:
                    response_from_questions = create_test_question_via_http(
                        self.client,
                        survey['url'],
                        question_type)

                    self.assertEqual(
                        response_from_questions.status_code,
                        201,
                        response_from_questions.data)

            page_url = response_from_surveys.data["next"]


class AnswerActViewSetTestCase(TestCase):
    def test_post_answer_acts_anon(self):
        response = self.client.post(path="/api/v1/actors/")
        self.assertEqual(response.status_code, 201)

        actor_url = response.data["url"]
        response = self.client.post(path="/api/v1/sessions/", data={
            "actor": actor_url,
        })
        self.assertEqual(response.status_code, 201)

        session_url = response.data["url"]
        questions_for_skip = []
        response_options_page_url = "/api/v1/responses/"
        while response_options_page_url:
            response_options = self.client.get(
                path=response_options_page_url)
            self.assertEqual(response.status_code, 201)

            response_options_data = response_options.data["results"]

            for response_option in response_options_data:
                question = response_option["question"]
                if question["pk"] in questions_for_skip:
                    continue

                response = self.client.post(path="/api/v1/answers/", data={
                    "response": response_option["url"],
                    "session": session_url,
                })
                self.assertEqual(response.status_code, 201)
                self.assertEqual(
                    response.data["response"]["url"], response_option["url"])
                self.assertEqual(response.data["session"]["url"], session_url)

                if question["type"] in ["one", "text"]:
                    questions_for_skip.append(question["pk"])

            response_options_page_url = response_options.data["next"]

    def test_get_answer_acts_with_empty_query_params(self):
        create_test_surveys_questions_and_response_options_via_model()
        response = self.client.get(path=f"/api/v1/answers/")
        self.assertEqual(response.status_code, 400, response.content)

    def test_get_answer_acts_by_query_param_actor_anon(self):
        create_test_surveys_questions_and_response_options_via_model()
        actors, sessions, answers = create_test_actors_sessions_and_answers_via_api()

        for actor in actors:
            response = self.client.get(path=f"/api/v1/answers/?actor={actor.pk}")
            self.assertEqual(response.status_code, 200, response.content)
            for answer in response.data["results"]:
                self.assertEqual(
                    answer["session"]["actor"]["pk"], str(actor.pk))

    def test_get_answer_acts_by_query_param_session_anon(self):
        create_test_surveys_questions_and_response_options_via_model()
        actors, sessions, answers = create_test_actors_sessions_and_answers_via_api()

        for session in sessions:
            response = self.client.get(
                path=f"/api/v1/answers/?session={session.pk}")
            self.assertEqual(response.status_code, 200, response.content)
            for answer in response.data["results"]:
                self.assertEqual(answer["session"]["pk"], str(session.pk))

    def test_get_answer_acts_by_query_param_question_anon(self):
        create_test_surveys_questions_and_response_options_via_model()
        actors, sessions, answers = create_test_actors_sessions_and_answers_via_api()

        for db_answer in answers:
            response = self.client.get(
                path=f"/api/v1/answers/?question={db_answer.response.question.pk}")
            self.assertEqual(response.status_code, 200, response.content)
            for answer in response.data["results"]:
                self.assertEqual(
                    answer["response"]["question"]["pk"],
                    db_answer.response.question.pk)
