from .utils import defensive_exception


class apply_defense(object):
    '''
    '''
    def __init__(self, return_value=None, return_statement=True, message=None):
        self.return_value = return_value
        self.return_statement = return_statement
        self.message = message

    def __call__(self, function_with_defense):
        def defensive_wrapper(*args, **kwargs):
            '''
            '''
            try:
                return function_with_defense(*args, **kwargs)
            except Exception as e:
                if self.return_value is None:
                    return_value_equals = e
                else:
                    return_value_equals = self.return_value
                if self.return_statement is True:
                    return defensive_exception(function_with_defense.__name__,
                                               e, return_value_equals,
                                               self.message)
                else:
                    raise defensive_exception(function_with_defense.__name__,
                                              e, return_value_equals,
                                              self.message)
        return defensive_wrapper