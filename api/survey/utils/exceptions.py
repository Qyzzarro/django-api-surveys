from django.core.exceptions import BadRequest

class NumberExcess(BaseException):
    pass

class EmptyQueryParamsException(BadRequest):
    pass

class WrongQueryParamsException(BadRequest):
    pass

class WrongDateOrderException(BaseException):
    pass

class BeginDateEditException(BaseException):
    pass