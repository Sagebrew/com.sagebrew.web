from .utils import defensive_exception


def apply_defense(function_with_defense, return_value=None,
                  return_statement=True, message=None):
    '''
    '''
    def defensive_wrapper(*args, **kwargs):
        '''
        '''
        try:
            return function_with_defense(*args, **kwargs)
        except Exception as e:
            if return_value is None:
                return_value_equals = e
            else:
                return_value_equals = return_value
            if(return_statement is True):
                return defensive_exception(function_with_defense.__name__, e,
                                           return_value_equals, message)
            else:
                raise defensive_exception(function_with_defense.__name__, e,
                                          return_value_equals, message)
    return defensive_wrapper