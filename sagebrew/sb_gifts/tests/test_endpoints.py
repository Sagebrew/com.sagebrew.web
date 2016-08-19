from uuid import uuid1

from django.contrib.auth.models import User
from django.core.cache import cache

from neomodel import db
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Address
from sb_registration.utils import create_user_util_test
from sb_missions.neo_models import Mission
from sb_quests.neo_models import Quest
from sb_gifts.neo_models import Product, Giftlist


class GiftlistEndpointTest(APITestCase):
    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        db.cypher_query(query)
        cache.clear()
        self.unit_under_test_name = 'quest'
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.quest.editors.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        self.address = Address(
            street="125 Glenwood Drive",
            city="Walled Lake", state="Michigan",
            postal_code="48390",
            country="USA", county="Oakland",
            congressional_district=11, validated=True).save()
        self.quest.address.connect(self.address)
        cache.clear()
        self.mission = Mission(owner_username=self.pleb.username,
                               title=str(uuid1()),
                               focus_name="advocacy",
                               location_name="11").save()
        self.quest.missions.connect(self.mission)
        self.giftlist = Giftlist().save()
        self.giftlist.mission.connect(self.mission)
        self.email2 = "bounce@simulator.amazonses.com"
        self.pleb2 = create_user_util_test(self.email2)
        self.user2 = User.objects.get(email=self.email2)

    def test_get_unauthorized(self):
        url = reverse("mission-giftlist",
                      kwargs={"object_uuid": self.mission.object_uuid})
        res = self.client.get(url)

        self.assertEqual(res.data['id'], self.giftlist.object_uuid)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("mission-giftlist",
                      kwargs={"object_uuid": self.mission.object_uuid})

        res = self.client.get(url)

        self.assertEqual(res.data['id'], self.giftlist.object_uuid)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update(self):
        product = Product(vendor_id="00000000").save()
        self.client.force_authenticate(user=self.user)
        url = reverse("mission-giftlist",
                      kwargs={"object_uuid": self.mission.object_uuid})
        data = {
            "product_ids": [product.vendor_id]
        }

        res = self.client.put(url, data=data, format="json")

        self.assertEqual(res.data['products'][0]['id'], product.object_uuid)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.delete()

    def test_update_remove(self):
        product = Product(vendor_id="00000000").save()
        self.client.force_authenticate(user=self.user)
        url = reverse("mission-giftlist",
                      kwargs={"object_uuid": self.mission.object_uuid})
        data = {
            "product_ids": []
        }
        product.giftlist.connect(self.giftlist)

        res = self.client.put(url, data=data, format="json")

        self.assertEqual(res.data['products'], [])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.delete()
