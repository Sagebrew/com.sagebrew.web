import time
import stripe
from uuid import uuid1

from django.conf import settings
from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_goals.neo_models import Goal
from sb_donations.neo_models import Donation
from sb_quests.neo_models import PoliticalCampaign, Position

from sb_quests.tasks import release_funds_task, release_single_donation_task


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

    def test_release_funds_goal_completed(self):
        test_goal = Goal().save()
        test_goal.campaign.connect(self.campaign)
        test_donation = Donation(amount=100,
                                 owner_username=self.pleb.username,
                                 completed=True).save()
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

    def test_release_funds_pleb_does_not_exist(self):
        test_goal = Goal().save()
        test_goal.campaign.connect(self.campaign)
        test_donation = Donation(amount=100,
                                 owner_username=str(uuid1())).save()
        test_goal.donations.connect(test_donation)
        test_donation.donated_for.connect(test_goal)
        data = {
            "goal_uuid": test_goal.object_uuid
        }
        res = release_funds_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, Exception)


class TestReleaseSingleDonation(TestCase):
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
        self.position = Position(level="local").save()
        self.campaign.position.connect(self.position)
        self.position.campaigns.connect(self.campaign)
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

    def test_release_single_donation(self):
        test_donation = Donation(amount=100,
                                 owner_username=self.pleb.username).save()
        self.campaign.donations.connect(test_donation)
        test_donation.campaign.connect(self.campaign)
        res = release_single_donation_task.apply_async(
            kwargs={"donation_uuid": test_donation.object_uuid})
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        test_donation.refresh()
        self.assertTrue(test_donation.completed)

    def test_release_single_donation_completed(self):
        test_donation = Donation(amount=100,
                                 owner_username=self.pleb.username,
                                 completed=True).save()
        self.campaign.donations.connect(test_donation)
        test_donation.campaign.connect(self.campaign)
        res = release_single_donation_task.apply_async(
            kwargs={"donation_uuid": test_donation.object_uuid})
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_release_single_donation_pleb_does_not_exist(self):
        test_donation = Donation(amount=100,
                                 owner_username=str(uuid1())).save()
        self.campaign.donations.connect(test_donation)
        test_donation.campaign.connect(self.campaign)
        res = release_single_donation_task.apply_async(
            kwargs={"donation_uuid": test_donation.object_uuid})
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, Exception)

    def test_release_single_donation_campaign_does_not_exist(self):
        test_donation = Donation(amount=100,
                                 owner_username=self.pleb.username).save()
        res = release_single_donation_task.apply_async(
            kwargs={"donation_uuid": test_donation.object_uuid})
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, Exception)
