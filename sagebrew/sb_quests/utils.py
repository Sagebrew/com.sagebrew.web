import stripe

from django.conf import settings
from django.template.loader import render_to_string

from neomodel import (db, DoesNotExist)

from api.utils import spawn_task
from plebs.neo_models import Pleb
from plebs.tasks import send_email_task
from sb_donations.neo_models import Donation

from .neo_models import Campaign


def release_funds(goal_uuid):
    from sb_donations.serializers import DonationSerializer
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        query = 'MATCH (g:Goal {object_uuid:"%s"})-[:RECEIVED]->(d:Donation), ' \
                '(g)-[:ASSOCIATED_WITH]->(c:Campaign) ' \
                'RETURN d, c' % goal_uuid
        res, _ = db.cypher_query(query)
        campaign = Campaign.inflate(res[0][1])
        for donation in res:
            donation_node = Donation.inflate(donation[0])
            if donation_node.completed:
                continue
            try:
                donor = Pleb.get(username=donation_node.owner_username)
            except (Pleb.DoesNotExist, DoesNotExist) as e:
                return e
            stripe.Charge.create(
                customer=donor.stripe_customer_id,
                amount=donation_node.amount,
                currency='usd',
                description='Quest Donation',
                destination=campaign.stripe_id,
                application_fee=int(
                    (donation_node.amount * (
                        campaign.application_fee +
                        settings.STRIPE_TRANSACTION_PERCENT)) + 30)
            )
            donation_node.completed = True
            donation_node.save()
            serialized_donation = DonationSerializer(donation_node).data
            serialized_donation['first_name'] = campaign.first_name
            serialized_donation['last_name'] = campaign.last_name
            email_data = {
                "to": donor.email, "subject": "Donation Release",
                "source": "support@sagebrew.com",
                "html_content": render_to_string(
                    "email_templates/email_donation_release.html",
                    serialized_donation)
            }
            spawn_task(send_email_task, email_data)
        return True
    except (stripe.CardError, stripe.APIConnectionError, stripe.StripeError,
            stripe.APIError) as e:
        return e


def release_single_donation(donation_uuid):
    from sb_donations.serializers import DonationSerializer
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        query = 'MATCH (d:Donation {object_uuid:"%s"}) return d' % \
                donation_uuid
        res, _ = db.cypher_query(query)
        donation = Donation.inflate(res.one)
        if donation.completed:
            return True
        try:
            campaign = Campaign.get(Donation.get_campaign(donation_uuid))
        except (Campaign.DoesNotExist, DoesNotExist) as e:
            return e
        try:
            donor = Pleb.get(username=donation.owner_username)
        except (Pleb.DoesNotExist, DoesNotExist) as e:
            return e
        charge = stripe.Charge.create(
            customer=donor.stripe_customer_id,
            amount=donation.amount,
            currency="usd",
            description="Quest Donation",
            destination=campaign.stripe_id,
            application_fee=int(
                (donation.amount * (campaign.application_fee +
                                    settings.STRIPE_TRANSACTION_PERCENT)) + 30)
        )
        donation.completed = True
        donation.save()
        serialized_donation = DonationSerializer(donation).data
        serialized_donation['first_name'] = campaign.first_name
        serialized_donation['last_name'] = campaign.last_name
        email_data = {
            "to": donor.email, "subject": "Donation Release",
            "source": "support@sagebrew.com",
            "html_content": render_to_string(
                "email_templates/email_donation_release.html",
                serialized_donation)
        }
        spawn_task(send_email_task, email_data)
        return charge
    except (stripe.CardError, stripe.APIConnectionError, stripe.StripeError,
            stripe.APIError) as e:
        return e
