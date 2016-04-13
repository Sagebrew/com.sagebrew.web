import pytz
import stripe
import datetime
import logging
from json import dumps
from copy import deepcopy

from django.conf import settings
from django.utils import six

from rest_framework import serializers
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

from py2neo.cypher.error.transaction import CouldNotCommit, ClientError
from neomodel.exception import CypherException, DoesNotExist
from neomodel import db

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
    if isinstance(exc, CypherException) or isinstance(exc, IOError) \
            or isinstance(exc, CouldNotCommit) or isinstance(exc, ClientError):
        data = errors.CYPHER_EXCEPTION
        logger.exception("%s Cypher Exception" % context['view'])
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc, IndexError):
        data = errors.CYPHER_INDEX_EXCEPTION
        logger.exception("%s Index Exception" % context['view'])
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc, ValueError):
        data = errors.JSON_ERROR_EXCEPTION
        logger.exception("%s JSON Exception" % context['view'])
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc, stripe.APIConnectionError):
        data = errors.STRIPE_CONNECTION_ERROR
        logger.exception("%s Stripe API Connection Error" % context['view'])
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc, stripe.APIError):
        data = errors.STRIPE_CONNECTION_ERROR
        logger.exception("%s Stripe API Error" % context['view'])
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc, DoesNotExist):
        request = context.get('request', None)
        logger.exception("%s Does Not Exist" % context['view'])
        if request is not None:
            if request.method == 'DELETE':
                return Response({"detail": None,
                                 "status": status.HTTP_204_NO_CONTENT},
                                status=status.HTTP_204_NO_CONTENT)
        data = errors.DOES_NOT_EXIST_EXCEPTION
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    if isinstance(exc, serializers.ValidationError):
        return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)

    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code
        response.data['detail'] = response.data.get(
            'detail', "Sorry, no details available.")
        error = {}
        response_data = deepcopy(response.data)
        for k in response_data:
            if k != 'status_code' and k != 'detail':
                error[k] = [{"code": error_value, "message": error_value}
                            for error_value in response_data[k]]
        if error:
            response.data['detail'] = dumps(error)

    return response


def get_ordering(sort_by):
    ordering = ""
    if '-' in sort_by:
        ordering = "DESC"
        sort_by = sort_by.replace('-', '')
    if sort_by == "created" or sort_by == "last_edited_on":
        sort_by = "ORDER BY res.%s" % sort_by
    else:
        sort_by = ""

    return sort_by, ordering


def get_tagged_as(tagged_as):
    if tagged_as == '' or tagged_as not in settings.BASE_TAGS:
        return ""
    return "-[:TAGGED_AS]->(t:Tag {name:'%s'})" % tagged_as


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
                additional_params = "AND res.%s %s %s" % (
                    query_property, query_operation, query_condition)
        else:
            raise KeyError
    return additional_params


class NeoQuerySet(object):
    def __init__(self, model=None, query=None, using=None, hints=None,
                 distinct=None, descending=None, query_order=None):
        self.model = model
        self.distinct = distinct
        self.descending = descending
        self._db = using
        self._hints = hints or {}
        self.query = query or "(res:%s)" % \
                              self.model.__name__
        self.query_order = query_order or ""
        self._result_cache = None
        self._sticky_filter = False
        self._for_write = False
        self._prefetch_related_lookups = []
        self._prefetch_done = False
        self._known_related_objects = {}  # {rel_field, {pk: rel_obj}}
        self._fields = None

    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results.
        """
        if not isinstance(k, (slice,) + six.integer_types):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0)) or
                (isinstance(k, slice) and (k.start is None or k.start >= 0) and
                 (k.stop is None or k.stop >= 0))), \
            "Negative indexing is not supported."
        if isinstance(k, slice):
            if k.start is not None:
                start = int(k.start)
            else:
                start = 0
            if k.stop is not None:
                stop = int(k.stop)
            else:
                stop = 0
            limit = stop - start
            exe_query = "MATCH %s WITH %s res %s %s " \
                        "RETURN res " \
                        "SKIP %d LIMIT %d" % (
                            self.query, self.is_distinct(), self.query_order,
                            self.reverse_order(), start, limit)
            qs, _ = db.cypher_query(exe_query)
            [row[0].pull() for row in qs]
            qs = [self.model.inflate(neoinstance[0]) for neoinstance in qs]
            return qs[::k.step] if k.step else qs
        qs, _ = db.cypher_query("MATCH %s RETURN res SKIP %d LIMIT %d" % (
            self.query, k, 1))
        [row[0].pull() for row in qs]
        return [self.model.inflate(neoinstance[0]) for neoinstance in qs][0]

    def count(self):
        res, _ = db.cypher_query("MATCH %s RETURN COUNT(%sres)" %
                                 (self.query, self.is_distinct()))
        return res.one

    def filter(self, query_filter):
        return self._filter_or_exclude(query_filter)

    def _filter_or_exclude(self, query_filter):
        return self._clone("%s %s" % (self.query, query_filter))

    def order_by(self, query_order):
        return self._clone(self.query, query_order=query_order)

    def is_distinct(self):
        if self.distinct:
            return "DISTINCT "
        else:
            return ""

    def reverse_order(self):
        if self.descending:
            return "DESC"
        else:
            return ""

    def _clone(self, query, query_order=None):
        clone = self.__class__(
            model=self.model, query=query, using=self._db,
            hints=self._hints, distinct=self.distinct,
            descending=self.descending,
            query_order=query_order or self.query_order)
        clone._for_write = self._for_write
        clone._prefetch_related_lookups = self._prefetch_related_lookups[:]
        clone._known_related_objects = self._known_related_objects
        clone._fields = self._fields

        return clone
