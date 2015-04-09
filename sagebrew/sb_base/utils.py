import logging
from json import dumps

from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

from sagebrew import errors

from neomodel.exception import CypherException

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
                  'exception': 'Unhandled Exception'}
    if message is not None:
        error_dict["message"] = message
    logger.critical(dumps(error_dict))
    logger.exception("defensive exception handler: ")

    return return_value


def custom_exception_handler(exc, context):
    if isinstance(exc, CypherException) or isinstance(exc, IOError):
        data = errors.CYPHER_EXCEPTION
        logger.exception("%s Cypher Exception" % context['view'])
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code
        if "developer_message" not in response.data:
            response.data['developer_message'] = "Sorry we don't currently " \
                                                 "have a suggestion for this " \
                                                 "issue. Please feel free to " \
                                                 "ping us at " \
                                                 "support@sagebrew.com and " \
                                                 "let us know what you're " \
                                                 "seeing."

    return response

