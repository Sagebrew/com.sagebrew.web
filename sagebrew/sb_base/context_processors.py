from os import environ
import json
from django.conf import settings

from neomodel import CypherException, DoesNotExist

from plebs.serializers import PlebSerializerNeo
from plebs.neo_models import Pleb


def js_settings(request):

    data = {
        'api': {
            'google_maps': environ.get('GOOGLE_MAPS_JS'),
            'stripe': settings.STRIPE_PUBLIC_KEY
        },
        'google_maps': environ.get('GOOGLE_MAPS_JS'),
        'user': {},
        'static_url': settings.STATIC_URL
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

    js_settings_output = "var SB_APP_SETTINGS = "
    js_settings_output += json.dumps(data)
    js_settings_output += ";"

    return {
        'js_settings': js_settings_output,
    }
