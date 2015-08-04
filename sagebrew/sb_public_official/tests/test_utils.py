from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb, Address
from sb_registration.utils import create_user_util_test

from sb_public_official.utils import (determine_reps)
from sb_public_official.neo_models import PublicOfficial


class TestPublicOfficialUtils(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.save()
        self.president = PublicOfficial(title='President').save()
        self.senator = PublicOfficial(state="MI", district=0).save()
        self.house_rep = PublicOfficial(state="MI", district=11).save()
        self.address = Address(street="3295 Rio Vista St",
                               city="Commerce Township", state="MI",
                               postal_code="48382", country="US",
                               congressional_district="11").save()
        self.pleb.address.connect(self.address)

    def test_determine_reps(self):
        res = determine_reps(self.pleb.username)

        self.assertTrue(res)
        self.assertTrue(self.pleb.senators.is_connected(self.senator))
        self.assertTrue(self.pleb.house_rep.is_connected(self.house_rep))
        self.assertTrue(self.pleb.president.is_connected(self.president))
