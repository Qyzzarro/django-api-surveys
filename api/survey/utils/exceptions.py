from django.core.exceptions import BadRequest

class NumberExcess(RuntimeError):
    pass

class EmptyQueryParamsException(BadRequest):
    pass

class WrongQueryParamsException(BadRequest):
    pass

class WrongDateOrderException(RuntimeError):
    pass

class BeginDateEditTryException(RuntimeError):
    pass

class WrongChoiseException(RuntimeError):
    pass