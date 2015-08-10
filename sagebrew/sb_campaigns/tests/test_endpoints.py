import stripe
from uuid import uuid1

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db

from sb_privileges.neo_models import SBAction, Privilege
from plebs.neo_models import Pleb
from sb_updates.neo_models import Update
from sb_goals.neo_models import Goal, Round
from sb_registration.utils import create_user_util_test
from sb_donations.neo_models import Donation

from sb_campaigns.neo_models import PoliticalCampaign, Position


class CampaignEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'campaign'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        for camp in self.pleb.campaign.all():
            camp.delete()
        self.url = "http://testserver"
        self.campaign = PoliticalCampaign(
            biography='Test Bio', owner_username=self.pleb.username).save()
        self.round = Round().save()
        self.campaign.upcoming_round.connect(self.round)
        self.round.campaign.connect(self.campaign)
        self.campaign.owned_by.connect(self.pleb)
        self.campaign.accountants.connect(self.pleb)
        self.campaign.editors.connect(self.pleb)
        self.pleb.campaign_accountant.connect(self.campaign)
        self.pleb.campaign_editor.connect(self.campaign)
        cache.clear()
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY

    def test_unauthorized(self):
        url = reverse('campaign-list')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-detail',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.post(url, data={}, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        position = Position(name="Senator").save()
        url = reverse('campaign-list')
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_gain_intercom(self):
        self.client.force_authenticate(user=self.user)
        position = Position(name="Senator").save()
        action = SBAction(resource="intercom", permission="write").save()
        privilege = Privilege(name="quest").save()
        url = reverse('campaign-list')
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        self.client.post(url, data=data, format='json')
        position.delete()
        query = 'MATCH (a:Pleb {username:"%s"})-[:CAN]->' \
                '(b:SBAction {resource: "intercom"}) RETURN b' % (
                    self.pleb.username)
        res, _ = db.cypher_query(query)
        action.delete()
        privilege.delete()
        self.assertEqual(res.one.resource, "intercom")

    def test_create_gain_quest_privilege(self):
        self.client.force_authenticate(user=self.user)
        position = Position(name="Senator").save()
        action = SBAction(resource="intercom", permission="write").save()
        privilege = Privilege(name="quest").save()
        url = reverse('campaign-list')
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        self.client.post(url, data=data, format='json')
        position.delete()
        query = 'MATCH (a:Pleb {username:"%s"})-[:HAS]->' \
                '(b:SBAction {resource: "intercom"}) RETURN b' % (
                    self.pleb.username)
        res, _ = db.cypher_query(query)
        action.delete()
        privilege.delete()
        self.assertEqual(res.one.name, "quest")

    def test_create_paid(self):
        self.client.force_authenticate(user=self.user)
        session = self.client.session
        session['account_type'] = 'paid'
        session.save()

        position = Position(name="Senator").save()
        url = reverse('campaign-list')
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        campaign = PoliticalCampaign.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(campaign.application_fee, 0.021)

    def test_create_unpaid(self):
        self.client.force_authenticate(user=self.user)

        position = Position(name="Senator").save()
        url = reverse('campaign-list')
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        campaign = PoliticalCampaign.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(campaign.application_fee, 0.041)

    def test_create_active(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['active'], False)

    def test_create_website(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['website'], "fake campaign website")

    def test_create_profile_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['profile_pic'], None)

    def test_create_wallpaper_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['wallpaper_pic'], None)

    def test_create_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['url'],
                         'http://testserver/quests/' +
                         response.data['id'] + '/')

    def test_create_twitter(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['twitter'], "fake twitter link")

    def test_create_youtube(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['youtube'], "fake youtube link")

    def test_create_linkedin(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['linkedin'], "fake linkedin link")

    def test_create_rounds(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['rounds'], [])

    def test_create_upcoming_round(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['upcoming_round'],
                         PoliticalCampaign.get_upcoming_round(
                             response.data['id']))

    def test_create_vote_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['vote_count'], 0)

    def test_create_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['href'], self.url + reverse(
            'campaign-detail', kwargs={'object_uuid': response.data['id']}))

    def test_create_facebook(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['facebook'], "fake facebook link")

    def test_create_owner_username(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['owner_username'], "test_test")

    def test_create_position(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['position'], position.object_uuid)

    def test_create_active_goals(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['active_goals'], [])

    def test_create_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['type'], "politicalcampaign")

    def test_create_biography(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['biography'], "this is a test bio")

    def test_create_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['id'], response.data['id'])

    def test_create_updates(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        position = Position(name="Senator").save()
        data = {
            "biography": "this is a test bio",
            "facebook": "fake facebook link",
            "linkedin": "fake linkedin link",
            "youtube": "fake youtube link",
            "twitter": "fake twitter link",
            "website": "fake campaign website",
            "position": position.object_uuid
        }
        response = self.client.post(url, data=data, format='json')
        position.delete()
        self.assertEqual(response.data['updates'], [])

    def test_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-detail',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_take_quest_active(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-detail',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        self.campaign.active = False
        self.campaign.save()
        cache.clear()
        for active_round in self.campaign.active_round.all():
            self.campaign.active_round.disconnect(active_round)
        data = {
            'activate': True,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.campaign.active_round.is_connected(self.round))

    def test_update_biography(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-detail',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            "biography": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['biography'], data['biography'])

    def test_update_facebook(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-detail',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            "facebook": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.data['facebook'], data['facebook'])

    def test_update_linkedin(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-detail',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            "linkedin": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['linkedin'], data['linkedin'])

    def test_update_youtube(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-detail',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            "youtube": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['youtube'], data['youtube'])

    def test_update_twitter(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-detail',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            "twitter": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['twitter'], data['twitter'])

    def test_update_website(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-detail',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            "website": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['website'], data['website'])

    def test_update_wallpaper_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-detail',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            "wallpaper_pic": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['wallpaper_pic'], data['wallpaper_pic'])

    def test_update_profile_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-detail',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            "profile_pic": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['profile_pic'], data['profile_pic'])

    def test_accountants(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-accountants',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ['test_test'])

    def test_accountants_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-accountants',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        self.campaign.accountants.disconnect(self.pleb)
        self.campaign.owner_username = ""
        self.campaign.owned_by.disconnect(self.pleb)
        self.campaign.save()
        response = self.client.get(url)

        self.assertEqual(response.data['detail'], "You do not have permission "
                                                  "to perform this action.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_accountants(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-remove-accountants',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        new_pleb = Pleb(username=str(uuid1())).save()
        data = {
            "profiles": ['test_test', new_pleb.username]
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully removed '
                                                  'specified accountants '
                                                  'from your campaign.')

    def test_add_accountants(self):
        self.client.force_authenticate(user=self.user)
        new_pleb = Pleb(username=str(uuid1())).save()
        url = reverse('campaign-add-accountants',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            "profiles": ['test_test', new_pleb.username]
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully added '
                                                  'specified users to '
                                                  'your campaign accountants.')

    def test_editors(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-editors',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ['test_test'])

    def test_editors_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-editors',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        self.campaign.editors.disconnect(self.pleb)
        self.campaign.owner_username = ""
        self.campaign.owned_by.disconnect(self.pleb)
        self.campaign.save()
        response = self.client.get(url)

        self.assertEqual(response.data['detail'], "You do not have permission "
                                                  "to perform this action.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_editors(self):
        self.client.force_authenticate(user=self.user)
        new_pleb = Pleb(username=str(uuid1())).save()
        url = reverse('campaign-remove-editors',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            "profiles": ['test_test', new_pleb.username]
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully removed '
                                                  'specified editors '
                                                  'from your campaign.')

    def test_add_editors(self):
        self.client.force_authenticate(user=self.user)
        new_pleb = Pleb(username=str(uuid1())).save()
        url = reverse('campaign-add-editors',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            "profiles": ['test_test', new_pleb.username]
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully added '
                                                  'specified users '
                                                  'to your campaign.')

    def test_vote(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-vote',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            'vote_type': 1
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['detail'])

    def test_rounds(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('round-list',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_updates(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-list',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_goals(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-list',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_goals_create(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-list',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            'title': 'This is a test goal',
            'summary': 'This is a test summary',
            'description': 'This is a test description',
            'pledged_vote_requirement': 100,
            'monetary_requirement': 1000
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_goals_create_unauthorized(self):
        self.campaign.editors.disconnect(self.pleb)
        self.campaign.owned_by.disconnect(self.pleb)
        self.campaign.accountants.disconnect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-list',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            'title': 'This is a test goal',
            'summary': 'This is a test summary',
            'description': 'This is a test description',
            'pledged_vote_requirement': 100,
            'monetary_requirement': 1000
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.data['detail'], "Authentication "
                                                  "credentials were not "
                                                  "provided.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_goals_create_invalid(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-list',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            'summary': 'This is a test summary',
            'description': 'This is a test description',
            'pledged_vote_requirement': 100,
            'monetary_requirement': 1000
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.data['title'], ['This field is required.'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_donation_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-donation-data',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_donation_data_with_donations(self):
        donation = Donation(amount=100, completed=False,
                            owner_username=self.pleb.username).save()
        self.campaign.donations.connect(donation)
        donation.campaign.connect(self.campaign)
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-donation-data',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_donations(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-donations',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_donation_create(self):
        self.client.force_authenticate(user=self.user)
        active_round = Round(active=True).save()
        target_goal = Goal(monetary_requirement=1000, target=True).save()
        self.campaign.goals.connect(target_goal)
        self.campaign.active_round.connect(active_round)
        url = reverse('campaign-donations',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            'amount': 1000
        }
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_donation_create_value_too_high(self):
        self.client.force_authenticate(user=self.user)
        active_round = Round(active=True).save()
        target_goal = Goal(monetary_requirement=1000, target=True).save()
        self.campaign.goals.connect(target_goal)
        self.campaign.active_round.connect(active_round)
        url = reverse('campaign-donations',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            'amount': 2700000
        }
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_donation_create_invalid_form(self):
        self.client.force_authenticate(user=self.user)
        active_round = Round(active=True).save()
        target_goal = Goal(monetary_requirement=1000, target=True).save()
        self.campaign.goals.connect(target_goal)
        self.campaign.active_round.connect(active_round)
        url = reverse('campaign-donations',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            'amount': 10.01
        }
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['amount'],
                         ['A valid integer is required.'])

    def test_donation_create_two_goals(self):
        self.client.force_authenticate(user=self.user)
        active_round = Round(active=True).save()
        next_goal = Goal(monetary_requirement=3000, target=False,
                         total_required=4000).save()
        target_goal = Goal(monetary_requirement=1000, target=True,
                           total_required=1000).save()
        target_goal.next_goal.connect(next_goal)
        next_goal.previous_goal.connect(target_goal)
        active_round.goals.connect(target_goal)
        active_round.goals.connect(next_goal)
        self.campaign.goals.connect(next_goal)
        self.campaign.goals.connect(target_goal)
        self.campaign.active_round.connect(active_round)
        url = reverse('campaign-donations',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            'amount': 4000
        }
        response = self.client.post(url, data=data, format='json')
        donation = self.campaign.donations.all()[0]
        self.assertTrue(target_goal.donations.is_connected(donation))
        self.assertTrue(next_goal.donations.is_connected(donation))
        self.assertTrue(donation.applied_to.is_connected(target_goal))
        self.assertTrue(donation.applied_to.is_connected(next_goal))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_donation_create_three_goals(self):
        self.client.force_authenticate(user=self.user)
        active_round = Round(active=True).save()
        next_goal = Goal(monetary_requirement=3000, target=False,
                         total_required=4000).save()
        next_goal2 = Goal(monetary_requirement=60000, target=False,
                          total_required=67000).save()
        target_goal = Goal(monetary_requirement=1000, target=True,
                           total_required=1000).save()
        target_goal.next_goal.connect(next_goal)
        next_goal.previous_goal.connect(target_goal)
        next_goal.next_goal.connect(next_goal2)
        next_goal2.previous_goal.connect(next_goal)
        active_round.goals.connect(target_goal)
        active_round.goals.connect(next_goal)
        self.campaign.goals.connect(next_goal)
        self.campaign.goals.connect(target_goal)
        self.campaign.goals.connect(next_goal2)
        self.campaign.active_round.connect(active_round)
        url = reverse('campaign-donations',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            'amount': 4000
        }
        response = self.client.post(url, data=data, format='json')
        donation = self.campaign.donations.all()[0]
        self.assertTrue(target_goal.donations.is_connected(donation))
        self.assertTrue(next_goal.donations.is_connected(donation))
        self.assertTrue(donation.applied_to.is_connected(target_goal))
        self.assertTrue(donation.applied_to.is_connected(next_goal))
        self.assertFalse(donation.applied_to.is_connected(next_goal2))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_create(self):
        self.client.force_authenticate(user=self.user)
        active_round = Round(active=True).save()
        target_goal = Goal(monetary_requirement=1000, target=True,
                           total_required=1000).save()
        active_round.goals.connect(target_goal)
        self.campaign.goals.connect(target_goal)
        self.campaign.active_round.connect(active_round)
        url = reverse('update-list',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            'content': 'Test Content for Update',
            'title': 'This is a test update'
        }
        response = self.client.post(url, data=data, format='json')
        update = Update.nodes.get(
            object_uuid=PoliticalCampaign.get_updates(
                self.campaign.object_uuid)[0])

        self.assertTrue(self.campaign.updates.is_connected(update))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_create_invalid(self):
        self.client.force_authenticate(user=self.user)
        active_round = Round(active=True).save()
        target_goal = Goal(monetary_requirement=1000, target=True,
                           total_required=1000).save()
        active_round.goals.connect(target_goal)
        self.campaign.goals.connect(target_goal)
        self.campaign.active_round.connect(active_round)
        url = reverse('update-list',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        data = {
            'content': 'Test Content for Update',
            'title': 'too short'
        }
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_create_render(self):
        self.client.force_authenticate(user=self.user)
        update = Update(content='test content', title='test title').save()
        self.campaign.updates.connect(update)
        url = reverse('update-render',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['results']['html'])

    def test_pledged_votes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-pledged-votes',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unassigned_goals(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-unassigned-goals',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_possible_helpers(self):
        self.client.force_authenticate(user=self.user)
        self.campaign.object_uuid = self.pleb.username
        self.campaign.save()
        url = reverse('campaign-possible-helpers',
                      kwargs={'object_uuid': self.campaign.object_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PositionEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'position'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.campaign = PoliticalCampaign(
            biography='Test Bio', owner_username=self.pleb.username).save()
        self.campaign.owned_by.connect(self.pleb)
        self.pleb.campaign.connect(self.campaign)
        self.campaign.accountants.connect(self.pleb)
        self.campaign.editors.connect(self.pleb)
        self.pleb.campaign_accountant.connect(self.campaign)
        self.pleb.campaign_editor.connect(self.campaign)
        self.position = Position(name="Senator").save()
        self.position.campaigns.connect(self.campaign)
        for camp in self.pleb.campaign.all():
            camp.delete()

    def test_unauthorized(self):
        url = reverse('position-list')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.post(url, data={}, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_detail_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['name'], 'Senator')

    def test_detail_campaigns(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['campaigns'],
                         [])

    def test_detail_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['href'], self.url + url)

    def test_detail_location(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.get(url)

        self.assertIsNone(response.data['location'])

    def test_detail_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['type'], 'position')

    def test_detail_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['id'], self.position.object_uuid)

    def test_put(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.put(url, {'name': 'House Rep'}, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.patch(url, {'name': 'House Rep'}, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-detail',
                      kwargs={'object_uuid': self.position.object_uuid})
        response = self.client.delete(url)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
