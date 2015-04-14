import pytz
import datetime
import logging
from json import dumps

from django.conf import settings

from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

from neomodel.exception import CypherException

from sagebrew import errors


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

    if isinstance(exc, IndexError):
        data = errors.CYPHER_INDEX_EXCEPTION
        logger.exception("%s Index Exception" % context['view'])
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response


def get_ordering(sort_by):
    ordering = ""
    if '-' in sort_by:
        ordering = "DESC"
        sort_by = sort_by.replace('-', '')
    if sort_by == "created" or sort_by == "last_edited_on":
        sort_by = "ORDER BY n.%s" % sort_by
    else:
        sort_by = ""

    return sort_by, ordering


def get_filter_params(filter_by, sb_instance):
    additional_params = ""
    if filter_by != "":
        query_param = filter_by.split(' ')
        query_property = query_param[0]
        if hasattr(sb_instance, query_property):
            # right now only support filtering by created/last_edited_on
            if(query_property == "created" or
                    query_property == "last_edited_on"):
                query_operation = settings.QUERY_OPERATIONS[
                    query_param[1]]
                query_condition = float(query_param[2])
                current_time = datetime.datetime.now(pytz.utc)
                time_diff = datetime.timedelta(seconds=query_condition)
                query_condition = (current_time -
                                   time_diff).strftime("%s")
                additional_params = "AND b.%s %s %s" % (
                    query_property, query_operation, query_condition)
        else:
            raise KeyError
    return additional_params