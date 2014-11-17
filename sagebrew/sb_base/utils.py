import logging
from json import dumps

logger = logging.getLogger('loggly_logs')


def defensive_exception(function_name, exception, return_value):
    logger.critical(dumps({'function': function_name,
                           'exception': 'Unhandled Exception',
                           'exception_dict': exception.__dict__}))
    logger.exception()

    return return_value
