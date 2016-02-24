from django.conf import settings
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
                if "/missions/" in request.path:
                    expand = True
                else:
                    expand = False
                return {
                    "free_missions": settings.FREE_MISSIONS,
                    "request_profile":
                        PlebSerializerNeo(Pleb.get(request.user.username),
                                          context={"request": request,
                                                   "expand": expand}).data}
            except(CypherException, IOError, Pleb.DoesNotExist, DoesNotExist):
                return default_response
        else:
            return default_response
    except AttributeError:
        # Caused when there is no user in the request or the request is a
        # WSGIRequest object
        return default_response
