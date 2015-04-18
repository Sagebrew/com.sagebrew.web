from neomodel.exception import CypherException

from .neo_models import Pleb
from .serializers import PlebSerializerNeo


def request_profile(request):
    # TODO should be able to greatly reduce latency by storing the serialized
    # version of the pleb in dynamo or the cache and accessing it from there
    default_response = {
        "request_profile":
            {
                "base_user": None,
                "href": None,
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
                pleb = Pleb.nodes.get(username=request.user.username)
                return {
                    "request_profile":
                        PlebSerializerNeo(pleb,
                                          context={"request": request}).data}
            except(CypherException, IOError):
                return default_response
        else:
            return default_response
    except AttributeError:
        # Caused when there is no user in the request or the request is a
        # WSGIRequest object
        return default_response
