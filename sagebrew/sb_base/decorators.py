from .utils import defensive_exception


def apply_defense(func):
    """
    apply_defense is the class that should used to cover any function that
    it is feared there may be exceptions that are unhandled. DO NOT put in
    custom code to handle except Exception as e. This decorator handles this
    for you and is thoroughly tested.
    If no exception is thrown it will always return exactly what the decorated
    function returns.
    """
    def defensive_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return defensive_exception(func.__name__, e, e)
    return defensive_wrapper
