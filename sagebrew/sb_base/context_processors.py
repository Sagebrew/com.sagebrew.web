from os import environ
import json
import stripe

from django.conf import settings

from neomodel import CypherException, DoesNotExist

from plebs.serializers import PlebSerializerNeo
from plebs.neo_models import Pleb

from sb_quests.neo_models import Quest


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
                pleb = Pleb.get(request.user.username)
                data['profile'] = PlebSerializerNeo(
                        pleb, context={"request": request, "expand": True}).data
                # Private not available in the serializer
                data['profile']['stripe_account'] = pleb.stripe_account
                data['profile']['stripe_customer_id'] = pleb.stripe_account
                if data['profile']['quest'] is not None:
                    if "quest" in request.path and "billing" in request.path:
                        # Private not available in the serializer
                        stripe.api_key = settings.STRIPE_SECRET_KEY
                        quest = Quest.get(pleb.username)
                        if quest.stripe_customer_id and \
                                quest.stripe_default_card_id:
                            customer = stripe.Customer.retrieve(
                                    quest.stripe_customer_id)
                            credit_card = customer.sources.retrieve(
                                    quest.stripe_default_card_id)
                            data['profile']['quest']['card'] = {
                                "brand": credit_card['brand'],
                                "last4": credit_card['last4'],
                                "exp_month": credit_card['exp_month'],
                                "exp_year": credit_card['exp_year']
                            }
                        else:
                            data['profile']['quest']['card'] = None
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
