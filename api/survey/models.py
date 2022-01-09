from datetime import date
import uuid

from django.db import models
from django.db.models.query import QuerySet

from api.survey.utils.exceptions import BeginDateEditException, NumberExcess, WrongDateOrderException


class SurveyModel(models.Model):
    header = models.TextField(blank=False, null=False)
    description = models.TextField(null=False, blank=True)
    begin_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    __first_begin_date = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__first_begin_date = self.begin_date

    def __str__(self) -> str:
        return self.header

    def save(self, *args, **kwargs) -> None:
        self.__block_begin_date()
        self.__check_order_of_begin_end_dates()
        return super().save(*args, **kwargs)

    def __block_begin_date(self) -> None:
        if not self.__first_begin_date in ['', None]:
            self.begin_date = self.__first_begin_date
        if self.__first_begin_date != self.begin_date:
            raise BeginDateEditException(
                "Edition of begin_date is not available.")

    def __check_order_of_begin_end_dates(self) -> None:
        if self.begin_date != None:
            if self.end_date != None:
                if self.begin_date > self.end_date:
                    raise WrongDateOrderException(
                        "Wrong order of begin end dates.")

    @property
    def is_published(self) -> None:
        is_published: bool = True
        if self.begin_date != None:
            is_published &= self.begin_date <= date.today()
        if self.end_date != None:
            is_published &= date.today() <= self.end_date
        return is_published

    class Meta:
        db_table = 'api_surveys'
        verbose_name = 'survey'
        verbose_name_plural = 'surveys'


class QuestionModel(models.Model):
    # TODO: Use class based choises
    TYPES = (
        ("one", "Only one answer"),
        ("many", "Many answers"),
        ("text", "Text answer"),
    )

    survey = models.ForeignKey(
        SurveyModel, on_delete=models.CASCADE,
        related_name='questions', null=False)
    type = models.TextField(choices=TYPES, blank=False, null=False)
    content = models.TextField(blank=True, null=False)

    def save(self, *args, **kwargs) -> None:
        super_result = super().save(*args, **kwargs)
        if self.type == "text":
            self.__create_fake_response_option()
        return super_result

    def get_response_options(self) -> QuerySet:
        return ResponseOptionModel.objects.filter(question=self)

    @property
    def have_fake_answer(self) -> bool:
        return bool(ResponseOptionModel.objects.filter(question=self, content="fake_answer").count())

    @property
    def is_published(self) -> None:
        return self.survey.is_published

    def __create_fake_response_option(self) -> None:
        ResponseOptionModel.objects.create(question=self, content="fake_answer")

    def __str__(self) -> str:
        return f"{self.survey}: {self.content[:50]}"

    class Meta:
        db_table = 'api_questions'
        verbose_name = 'question'
        verbose_name_plural = 'questions'


class ResponseOptionModel(models.Model):
    question = models.ForeignKey(
        QuestionModel, on_delete=models.CASCADE,
        related_name='response_options', null=False)
    content = models.TextField(blank=False, null=False)

    def save(self, *args, **kwargs) -> None:
        if self.question.type == "text":
            self.__check_number_of_response_options()
        return super().save(*args, **kwargs)

    @property
    def is_published(self) -> bool:
        return self.question.survey.is_published

    @property
    def type(self) -> str:
        return self.question.type

    def __check_number_of_response_options(self) -> None:
        if ResponseOptionModel.objects.filter(question=self.question).count() > 0:
            raise NumberExcess(
                f"This type of question ({self.question.type}) can't have extra response options.")

    def __str__(self) -> str:
        return f"{self.question}: \"{self.content[:50]}\""
    
    class Meta:
        db_table = 'api_response_options'
        verbose_name = 'response option'
        verbose_name_plural = 'response options'


class ActorModel(models.Model):
    unique_key = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    __first_unique_key = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__first_unique_key = self.unique_key

    def __str__(self) -> str:
        return f"{self.unique_key}"

    def __block_unique_key(self):
        if not self.unique_key in ("", None):
            self.unique_key = self.__first_unique_key

    def save(self, *args, **kwargs) -> None:
        self.__block_unique_key()
        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'api_actors'
        verbose_name = 'survey actor'
        verbose_name_plural = 'survey actors'


class SessionModel(models.Model):
    unique_key = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    __first_unique_key = None
    actor = models.ForeignKey(
        ActorModel, on_delete=models.CASCADE,
        null=False, related_name="sessions")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__first_unique_key = self.unique_key

    def __str__(self) -> str:
        return f"{self.unique_key}"

    def __block_unique_key(self):
        if not self.unique_key in ("", None):
            self.unique_key = self.__first_unique_key

    def save(self, *args, **kwargs) -> None:
        self.__block_unique_key()
        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'api_sessions'
        verbose_name = 'survey session'
        verbose_name_plural = 'survey sessions'


class AnswerActModel(models.Model):
    session = models.ForeignKey(
        SessionModel, on_delete=models.CASCADE,
        related_name="answer_acts", null=False)
    response = models.ForeignKey(
        ResponseOptionModel, null=False, on_delete=models.CASCADE,
        related_name="answer_acts")
    content = models.TextField(null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self):
        if self.response.question.type == "text":
            return f"{self.actor}-> {self.response.question}: {self.content[:50]}"
        else:
            return f"{self.actor}-> {self.response}"

    def save(self, *args, **kwargs) -> None:
        self.__check_number_of_answers()
        return super().save(*args, **kwargs)

    def __check_number_of_answers(self) -> None:
        if self.response.question.type in ["one", "text"]:
            if AnswerActModel.objects.filter(
                session=self.session,
                response__question=self.response.question,
            ).count() > 0:
                raise NumberExcess(
                    "Number of answers on this question in this session is exceeded")
        elif self.response.question.type in ["many"]:
            if AnswerActModel.objects.filter(
                session=self.session,
                response=self.response,
            ).count() > 0:
                raise NumberExcess(
                    "Number of answers on this question in this session is exceeded")

    class Meta:
        db_table = 'api_answer_acts'
        verbose_name = 'answer act'
        verbose_name_plural = 'answer acts'
