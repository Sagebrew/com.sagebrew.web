from django.core.cache import cache

from neomodel.exception import CypherException, DoesNotExist

from .neo_models import Pleb
from .serializers import PlebSerializerNeo


def request_profile(request):
    # TODO should be able to greatly reduce latency by storing the serialized
    # version of the pleb in dynamo or the cache and accessing it from there
    default_response = {
        "request_profile":
            {
                "href": None,
                "first_name": None,
                "last_name": None,
                "username": None,
                "profile_pic": None,
                "wallpaper_pic": None,
                "reputation": None,
                "privileges": [],
                "actions": [],
                "url": None
            }
    }
    try:
        if request.user.is_authenticated():
            try:
                profile = cache.get(request.user.username)
                if profile is None:
                    profile = Pleb.nodes.get(username=request.user.username)
                return {
                    "request_profile":
                        PlebSerializerNeo(profile,
                                          context={"request": request}).data}
            except(CypherException, IOError, Pleb.DoesNotExist, DoesNotExist):
                return default_response
        else:
            return default_response
    except AttributeError:
        # Caused when there is no user in the request or the request is a
        # WSGIRequest object
        return default_response
