from neomodel.exception import CypherException

from .neo_models import Pleb
from .serializers import PlebSerializerNeo


def request_profile(request):
    # TODO should be able to greatly reduce latency by storing the serialized
    # version of the pleb in dynamo or the cache and accessing it from there
    if request.user.is_authenticated():
        try:
            pleb = Pleb.nodes.get(username=request.user.username)
            return {
                "request_profile":
                    PlebSerializerNeo(pleb, context={"request": request}).data}
        except(CypherException, IOError):
            return {"request_profile": None}