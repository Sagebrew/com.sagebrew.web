import logging
from json import dumps

logger = logging.getLogger('loggly_logs')


def defensive_exception(function_name, exception, return_value, message=None):
    """
    defensive_exception is a utility that logs off an exception and then returns
    whatever the calling function wanted returned in the scenario. This function
    should be used for handling any unhandled exceptions and for any defensive
    code. This way we can test the handling of the exceptions.

    :param function_name: str
    :param exception: exception object
    :param return_value: duck typed
    :param message: str or dict
    :return: return_value
    """
    error_dict = {'function': function_name,
                  'exception': 'Unhandled Exception',
                  'exception_dict': exception.__dict__}
    if message is not None:
        error_dict["message"] = message
    logger.critical(dumps(error_dict))
    logger.exception("defensive exception handler: ")

    return return_value
