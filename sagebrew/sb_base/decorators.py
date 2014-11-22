from .utils import apply_defense_util

"""
    def __init__(self, return_value=None, message=None):
        self.return_value = return_value
        self.message = message

    def __call__(self, function_with_defense):
        def defensive_wrapper(*args, **kwargs):
            try:
                return function_with_defense(*args, **kwargs)
            except Exception as e:
                return apply_defense_util(function_with_defense.__name__, e,
                                          self.return_value, self.message)
        return defensive_wrapper
    """
def apply_defense(func):
    '''
    apply_defense is the class that should used to cover any function that
    it is feared there may be exceptions that are unhandled. DO NOT put in
    custom code to handle except Exception as e. This decorator handles this
    for you and is thoroughly tested.
    If no exception is thrown it will always return exactly what the decorated
    function returns.

    The decorator takes three optional arguments.
    If no arguments are passed to the decorator then in the case where an
    exception is thrown that was unhandled it will return the exception option
    to the function calling the decorated one.

    :param return_value
        This parameter is used to indicate what the decorated function would
        like returned in the case of an unhandled exception being thrown.
        If nothing is passed and an unhandled exception thrown then it will
        return the exception object. Otherwise if a value is passed that value
        shall be returned in the case that an unhandled exception is thrown.
    :param message
        This parameter allows the decorated function to pass an optional message
        it would like to get logged in the cause of an unhandled exception.
        This value can either be a string or a dictionary. In either case
        it will be converted to JSON and logged to the set logger.
    '''
    def defensive_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return apply_defense_util(func.__name__, e, e)
    return defensive_wrapper

