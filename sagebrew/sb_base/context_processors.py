from os import environ
import json
import stripe

from django.conf import settings
from django.core.cache import cache
from django.templatetags.static import static

from neomodel import CypherException, DoesNotExist

from plebs.serializers import PlebSerializerNeo
from plebs.neo_models import Pleb

from sb_quests.neo_models import Quest


def js_settings(request):
    data = {
        'api': {
            'google_maps': environ.get('GOOGLE_MAPS_JS'),
            'stripe': settings.STRIPE_PUBLIC_KEY,
            'liveaddress': settings.ADDRESS_AUTH_ID
        },
        'google_maps': environ.get('GOOGLE_MAPS_JS'),
        'user': {},
        'static_url': settings.STATIC_URL,
        "default_profile_pic": static('images/sage_coffee_grey-01.png'),
        'version': environ.get("SHA1", ""),
        'quest_promo_key': settings.PROMOTION_KEYS[0]
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
                    quest = Quest.get(pleb.username)
                    if "/quests/%s/" % quest.owner_username in request.path or \
                            "/quests/%s/" % quest.object_uuid in request.path:
                        data['profile']['quest']['is_owner'] = True
                    data['profile']['quest']['available_missions'] = False
                    if quest.account_type == "free":
                        data['profile']['quest']['free_quest'] = True
                        if len(quest.missions) >= settings.FREE_MISSIONS:
                            data['profile']['quest'][
                                'available_missions'] = True
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    if "quest" in request.path:
                        # If we're in a place where we're telling the user
                        # that their quest is inactive lets indicate that the
                        # quest has a card on file so they can activate
                        if quest.stripe_default_card_id is not None:
                            data['profile']['quest']['card_on_file'] = True
                        else:
                            data['profile']['quest']['card_on_file'] = False
                        data['profile']['quest'][
                            'account_type'] = quest.account_type
                    if "manage/banking" in request.path:
                        # TODO This is a interim solution while we create
                        # a webhook to accept updates from stripe on the
                        # verification process
                        account = stripe.Account.retrieve(quest.stripe_id)
                        data['profile']['quest'][
                            'stripe_identification_sent'] = \
                            quest.stripe_identification_sent
                        data['profile']['quest']['verification'] = {}
                        quest.account_verified = account[
                            'legal_entity']['verification']['status']
                        fields_needed = account[
                            'verification']['fields_needed']
                        if "legal_entity.verification.document" in \
                                fields_needed:
                            data['profile']['quest'][
                                'verification']['upload_id'] = True
                        if fields_needed is not None:
                            fields_needed = ", ".join(
                                [field.replace('legal_entity.', "").replace(
                                    '_', " ").title() for field in fields_needed
                                 if field in [
                                     'legal_entity.business_tax_id',
                                     'legal_entity.business_name']])

                        data['profile']['quest'][
                            'verification']['fields_needed'] = fields_needed
                        data['profile']['quest'][
                            'verification']['due_by'] = account[
                            'verification']['due_by']
                        disabled_reason = account[
                            'verification']['disabled_reason']
                        if disabled_reason is not None:
                            disabled_reason = disabled_reason.replace(
                                'rejected.', "").replace('_', " ").title()
                        data['profile']['quest'][
                            'verification']['disabled_reason'] = disabled_reason
                        quest.save()
                        cache.set('%s_quest' % quest.owner_username, quest)
                    if "quest" in request.path and "billing" in request.path:
                        # Private not available in the serializer
                        data['profile']['quest']['card'] = None
                        data['profile']['quest']['subscription'] = None
                        if quest.stripe_customer_id:
                            customer = stripe.Customer.retrieve(
                                quest.stripe_customer_id)
                            if quest.stripe_default_card_id:
                                credit_card = customer.sources.retrieve(
                                    quest.stripe_default_card_id)
                                data['profile']['quest']['card'] = {
                                    "brand": credit_card['brand'],
                                    "last4": credit_card['last4'],
                                    "exp_month": credit_card['exp_month'],
                                    "exp_year": credit_card['exp_year']
                                }
                            if quest.stripe_subscription_id is not None:
                                subscription = customer.subscriptions.retrieve(
                                    quest.stripe_subscription_id)

                                data['profile']['quest']['subscription'] = {
                                    "current_period_end": subscription[
                                        'current_period_end'],
                                    "current_period_start": subscription[
                                        'current_period_start'],
                                    "amount": subscription['plan']['amount']
                                }
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
