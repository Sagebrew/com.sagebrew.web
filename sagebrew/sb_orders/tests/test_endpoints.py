import stripe
import datetime
from uuid import uuid1

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db

from plebs.neo_models import Address
from plebs.serializers import PlebSerializerNeo
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question
from sb_questions.serializers import QuestionSerializerNeo
from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer
from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer
from sb_gifts.neo_models import Product, Giftlist
from sb_orders.neo_models import Order


class MissionEndpointTests(APITestCase):

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
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
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

    def test_list_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("orders-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['details'],
                         "Sorry we don't allow users to query all "
                         "Orders on the site.")

    def test_list_authorized(self):
        try:
            user = User.objects.get(username="tyler_wiersing")
            self.client.force_authenticate(user=user)
        except User.DoesNotExist:
            self.user.username = 'tyler_wiersing'
            self.user.save()
            self.client.force_authenticate(user=self.user)
        url = reverse("orders-list")
        response = self.client.get(url)

        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_authorized_orders(self):
        try:
            user = User.objects.get(username="tyler_wiersing")
            self.client.force_authenticate(user=user)
        except User.DoesNotExist:
            self.user.username = 'tyler_wiersing'
            self.user.save()
            self.client.force_authenticate(user=self.user)

        order = Order(completed=False, paid=True).save()
        url = reverse("orders-list")
        response = self.client.get(url)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], order.object_uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.delete()

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("orders-list")

        order_data = {
            "mission": self.mission.object_uuid,
            "product_ids": [],
            "total": 100
        }
        response = self.client.post(url, data=order_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], 'order')
        self.assertEqual(response.data['total'], 100)
        self.assertEqual(response.data['products'], [])

    def test_create_with_products(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("orders-list")

        product = Product().save()
        product.giftlist.connect(self.giftlist)

        order_data = {
            "mission": self.mission.object_uuid,
            "product_ids": [product.object_uuid],
            "total": 100
        }
        response = self.client.post(url, data=order_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], 'order')
        self.assertEqual(response.data['total'], 100)
        self.assertEqual(response.data['products'][0]['id'],
                         product.object_uuid)

    def test_create_invalid_total(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("orders-list")

        order_data = {
            "mission": self.mission.object_uuid,
            "product_ids": [],
            "total": 0
        }
        response = self.client.post(url, data=order_data, format="json")

        self.assertEqual(response.data['total'], ["Cannot be $0 or less"])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pay_order(self):
        self.client.force_authenticate(user=self.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        token = stripe.Token.create(
            card={
                "number": "4242424242424242",
                "exp_month": 12,
                "exp_year": (datetime.datetime.now() + datetime.timedelta(
                    days=3 * 365)).year,
                "cvc": '123'
            }
        )
        customer = stripe.Customer.create(
            description="Customer for %s" % self.pleb.username,
            card=token['id'],
            email=self.pleb.email
        )
        self.pleb.stripe_customer_id = customer['id']
        self.pleb.stripe_default_card_id = token['id']
        self.pleb.save()

        order = Order(completed=False, paid=True,
                      owner_username=self.pleb.username).save()

        url = reverse("orders-detail", kwargs={'object_uuid': order.object_uuid})

        order_data = {
            "mission": self.mission.object_uuid,
            "payment_method": self.pleb.stripe_default_card_id
        }
        response = self.client.put(url, data=order_data, format="json")

        print response
