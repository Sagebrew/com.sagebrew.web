import logging
from json import dumps

logger = logging.getLogger('loggly_logs')


def defensive_exception(function_name, exception, return_value, message=None):
    error_dict = {'function': function_name,
                  'exception': 'Unhandled Exception',
                  'exception_dict': exception.__dict__}
    if message is not None:
        error_dict["message"] = message
    logger.critical(dumps(error_dict))
    logger.exception("defensive exception handler: ")

    return return_value
