from django.conf import settings

from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ValidationError

from elasticsearch import Elasticsearch
from amazon.api import AmazonAPI

from sagebrew import errors
from api.utils import (spawn_task)
from api.alchemyapi import AlchemyAPI

from .tasks import update_search_query


class SearchViewSet(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        filter_type = self.request.query_params.get("filter", "general")
        query_param = self.request.query_params.get("query", "")
        search_type_dict = dict(settings.SEARCH_TYPES)
        alchemyapi = AlchemyAPI()
        response = alchemyapi.keywords("text", query_param)
        # this .get on a dict is a temporary work around for the alchemyapi
        # package not having any exception handling, this will keep us safe
        # from key errors caused by us hitting the alchemy endpoint too much
        # and using up our allowed requests
        keywords = response.get('keywords', [])
        # TODO surround ES query with proper exception handling and ensure
        # each one is handled correctly
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        # TODO run query_param through natural language processor, determine
        # if what they have searched is an email address or a name so that
        # the first search result is that user
        # TODO implement filtering on auto generated keywords from alchemyapi
        if filter_type is None or filter_type == 'general':
            res = es.search(
                index='full-search-base', size=50,
                body={
                    "query": {
                        "multi_match": {
                            "fields": settings.SEARCH_FIELDS,
                            "query": query_param,
                            "fuzziness": "AUTO",
                            "phrase_slop": 2
                        }
                    }
                })
        else:
            try:
                res = es.search(
                    index='full-search-base', size=50,
                    doc_type=search_type_dict[filter_type],
                    body={
                        "query": {
                            "multi_match": {
                                "fields": settings.SEARCH_FIELDS,
                                "query": query_param,
                                "fuzziness": "AUTO",
                                "phrase_slop": 2
                            }
                        }
                    })
            except KeyError:
                raise ValidationError("Invalid filter parameter")

        task_param = {"username": self.request.user.username,
                      "query_param": query_param,
                      "keywords": keywords}
        # we do not notify users if this task fails to spawn because it is
        # just for us later down the line
        spawn_task(task_func=update_search_query, task_param=task_param)
        return res['hits']['hits']

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
        except ValidationError:
            return Response(errors.QUERY_DETERMINATION_EXCEPTION,
                            status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(queryset)
        return self.get_paginated_response(page)


class AmazonProductSearchViewSet(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        amazon = AmazonAPI("AKIAI5PAWWJNUQPPXL3Q", "/XylsuBQopHlYC63+ZBjZ9HqEPmPHsH/9pMOPRjR", "sagebrew-20")
        # amazon = AmazonAPI(settings.AMAZON_ACCESS_KEY, settings.AMAZON_SECRET_KEY, settings.AMAZON_ASSOC_TAG)
        queryset = []
        query_param = self.request.query_params.get("query", "")
        if query_param:
            products = amazon.search_n(n=15, Keywords=query_param, SearchIndex="All")
            for product in products:
                queryset.append({
                    "title": product.title,
                    "image": product.large_image_url,
                    "price": product.price_and_currency[0],
                    "currency": product.price_and_currency[1],
                    "asin": product.asin,
                    "url": product.offer_url
                })
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
        except ValidationError:
            return Response(errors.QUERY_DETERMINATION_EXCEPTION,
                            status=status.HTTP_400_BAD_REQUEST)
        page = self.paginate_queryset(queryset)
        return self.get_paginated_response(page)
