import time
import stripe

from django.conf import settings
from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_goals.neo_models import Goal
from sb_donations.neo_models import Donation
from sb_campaigns.neo_models import PoliticalCampaign

from sb_campaigns.tasks import release_funds_task


class TestReleaseFundsTask(TestCase):
    def setUp(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.campaign = PoliticalCampaign(
            biography='Test Bio', owner_username=self.pleb.username).save()
        customer = stripe.Customer.create(
            description="a customer for testing release funds",
            source={
                "object": "card",
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": "2020",
                "csv": "123"
            }
        )
        account = stripe.Account.create(
            managed=True,
            country="US",
            email=self.pleb.email,
            external_account={
                "object": "bank_account",
                "country": "US",
                "currency": "usd",
                "routing_number": 110000000,
                "account_number": "000123456789",
            }
        )
        self.campaign.stripe_id = account['id']
        self.campaign.save()
        self.pleb.stripe_customer_id = customer['id']
        self.pleb.save()
        cache.delete(self.pleb.username)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_release_funds(self):
        test_goal = Goal().save()
        test_goal.campaign.connect(self.campaign)
        test_donation = Donation(amount=100,
                                 owner_username=self.pleb.username).save()
        test_goal.donations.connect(test_donation)
        test_donation.donated_for.connect(test_goal)
        data = {
            "goal_uuid": test_goal.object_uuid
        }
        res = release_funds_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        test_donation.refresh()
        self.assertTrue(test_donation.completed)
