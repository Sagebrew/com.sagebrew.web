import stripe

from neomodel import (db)

from .neo_models import Campaign

from plebs.neo_models import Pleb
from sb_donations.neo_models import Donation

from logging import getLogger
logger = getLogger('loggly_logs')


def release_funds(goal_uuid):
    stripe.api_key = "sk_test_4VQN8LrYMe8xbLH5v9kLMoKt"
    query = 'MATCH (g:Goal {object_uuid:"%s"})-[:RECEIVED]-(d:Donation), ' \
            '(g)-[:ASSOCIATED_WITH]->(c:Campaign) ' \
            'RETURN d, c' % goal_uuid
    res, _ = db.cypher_query(query)
    campaign = Campaign.inflate(res[0][1])
    for donation in res:
        donation_node = Donation.inflate(donation[0])
        if donation_node.completed:
            continue
        donor = Pleb.nodes.get(username=donation_node.owner_username)
        stripe.Charge.create(
            customer=donor.stripe_customer_id,
            amount=donation_node.amount,
            currency='usd',
            description='Quest Donation',
            destination=campaign,
            application_fee=int(donation_node.amount *
                                campaign.application_fee)
        )
        donation_node.completed = True
        donation_node.save()