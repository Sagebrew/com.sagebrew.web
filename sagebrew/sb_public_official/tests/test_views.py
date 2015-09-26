from django.core.cache import cache
from django.test import Client, TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status

from neomodel import DoesNotExist

from plebs.neo_models import Pleb
from sb_campaigns.neo_models import PoliticalCampaign
from sb_registration.utils import create_user_util_test


class PublicOfficialViews(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.client = Client()
        self.password = "testpassword"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        try:
            self.campaign = PoliticalCampaign.get(self.pleb.username)
        except (PoliticalCampaign.DoesNotExist, DoesNotExist):
            self.campaign = PoliticalCampaign(
                owner_username=self.pleb.username,
                object_uuid=self.pleb.username).save()
        self.pleb.campaign.connect(self.campaign)
        self.campaign.owned_by.connect(self.pleb)
        self.campaign.accountants.connect(self.pleb)
        self.campaign.editors.connect(self.pleb)
        self.pleb.completed_profile_info = True
        self.pleb.email_verified = True
        self.pleb.save()
        self.client.login(username=self.user.username, password=self.password)
        cache.set(self.pleb.username, self.pleb)

    def tearDown(self):
        self.campaign.delete()

    def test_quest_saga(self):
        url = reverse("quest_saga",
                      kwargs={'username': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quest_saga_with_biography(self):
        self.campaign.biography = "This is my new biography"
        self.campaign.save()
        url = reverse("quest_saga",
                      kwargs={'username': self.campaign.object_uuid})
        response = self.client.get(url)
        self.campaign.biography = None
        self.campaign.sav()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quest_saga_no_biography(self):
        self.campaign.biography = None
        self.campaign.save()
        url = reverse("quest_saga",
                      kwargs={'username': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quest_updates(self):
        url = reverse("quest_saga",
                      kwargs={'username': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quest_statistics(self):
        url = reverse("quest_stats",
                      kwargs={'username': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quest_moderators(self):
        url = reverse("quest_moderators",
                      kwargs={'username': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quest_search(self):
        url = reverse("rep_search_html",
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quest_edit_epic(self):
        url = reverse("quest_epic",
                      kwargs={'username': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quest_create_update(self):
        url = reverse("create_update",
                      kwargs={'username': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quest_manage_goals(self):
        url = reverse("manage_goals",
                      kwargs={'username': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
