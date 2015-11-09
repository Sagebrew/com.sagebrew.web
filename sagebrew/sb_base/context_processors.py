from os import environ
import json

from neomodel import CypherException, DoesNotExist

from plebs.serializers import PlebSerializerNeo
from plebs.neo_models import Pleb


def js_settings(request):

    data = {
        'google_maps': environ.get('GOOGLE_MAPS_JS'),
        'user': {}
    }
    try:
        if request.user.is_authenticated():
            data['user']['type'] = "auth"
            data['user']['username'] = request.user.username
            try:
                data['profile'] = PlebSerializerNeo(
                    Pleb.get(request.user.username),
                    context={"request": request}).data
            except(CypherException, IOError, Pleb.DoesNotExist, DoesNotExist):
                data['profile'] = None
        else:
            data['user']['type'] = "anon"

    except AttributeError:
        data['user']['type'] = "anon"

    settings = "var SB_APP_SETTINGS = "
    settings += json.dumps(data)
    settings += ";"

    return {
        'js_settings': settings,
    }
