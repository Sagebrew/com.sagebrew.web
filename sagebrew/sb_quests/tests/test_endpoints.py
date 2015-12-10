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
from sb_locations.neo_models import Location

from sb_quests.neo_models import Quest, Position


class QuestEndpointTests(APITestCase):
    def setUp(self):
        query = "match (n)-[r]-() delete n,r"
        db.cypher_query(query)
        self.unit_under_test_name = 'quest'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        for camp in self.pleb.campaign.all():
            camp.delete()
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.quest.editors.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        self.pleb.campaign_accountant.connect(self.quest)
        self.pleb.campaign_editor.connect(self.quest)
        cache.clear()
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY

    def test_unauthorized(self):
        url = reverse('quest-list')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
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
        self.assertEqual(SBAction.inflate(res.one).resource, "intercom")

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
                '(b:Privilege {name: "quest"}) RETURN b' % (
                    self.pleb.username)
        res, _ = db.cypher_query(query)
        action.delete()
        privilege.delete()
        self.assertEqual(Privilege.inflate(res.one).name, "quest")

    def test_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_take_quest_active(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        self.quest.active = False
        self.quest.save()
        cache.clear()
        data = {
            'activate': True,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['active'], True)

    def test_update_biography(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "biography": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['biography'], data['biography'])

    def test_update_biography_too_long(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "biography": "The first issues I encountered in my Quest was "
                         "with the short bio. The instructions in the text "
                         "box say there is a limit of 255 characters, but "
                         "another error comes up when I press submit that "
                         "says the limit is 150 characters. Just to text "
                         "things, I shortened it, this is waaaaay too long"
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_update_facebook(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "facebook": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.data['facebook'], data['facebook'])

    def test_update_linkedin(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "linkedin": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['linkedin'], data['linkedin'])

    def test_update_youtube(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "youtube": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['youtube'], data['youtube'])

    def test_update_twitter(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "twitter": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['twitter'], data['twitter'])

    def test_update_website(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "website": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['website'], data['website'])

    def test_update_wallpaper_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "wallpaper_pic": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['wallpaper_pic'], data['wallpaper_pic'])

    def test_update_profile_pic(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-detail',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "profile_pic": "this is an update"
        }
        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.data['profile_pic'], data['profile_pic'])

    def test_moderators(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-moderators',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ['test_test'])

    def test_moderators_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-moderators',
                      kwargs={'owner_username': self.quest.owner_username})
        self.quest.moderators.disconnect(self.pleb)
        self.quest.owner_username = ""
        self.quest.owned_by.disconnect(self.pleb)
        self.quest.save()
        response = self.client.get(url)

        self.assertEqual(response.data['detail'], "You do not have permission "
                                                  "to perform this action.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_moderators(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-remove-moderators',
                      kwargs={'owner_username': self.quest.owner_username})
        new_pleb = Pleb(username=str(uuid1())).save()
        data = {
            "profiles": ['test_test', new_pleb.username]
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully removed '
                                                  'specified moderators '
                                                  'from your campaign.')

    def test_add_moderators(self):
        self.client.force_authenticate(user=self.user)
        new_pleb = Pleb(username=str(uuid1())).save()
        url = reverse('quest-add-moderators',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "profiles": ['test_test', new_pleb.username]
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully added '
                                                  'specified users to '
                                                  'your campaign moderators.')

    def test_editors(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-editors',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ['test_test'])

    def test_editors_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('quest-editors',
                      kwargs={'owner_username': self.quest.owner_username})
        self.quest.editors.disconnect(self.pleb)
        self.quest.owner_username = ""
        self.quest.owned_by.disconnect(self.pleb)
        self.quest.save()
        response = self.client.get(url)

        self.assertEqual(response.data['detail'], "You do not have permission "
                                                  "to perform this action.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_editors(self):
        self.client.force_authenticate(user=self.user)
        new_pleb = Pleb(username=str(uuid1())).save()
        url = reverse('quest-remove-editors',
                      kwargs={'owner_username': self.quest.owner_username})
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
        url = reverse('quest-add-editors',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            "profiles": ['test_test', new_pleb.username]
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully added '
                                                  'specified users '
                                                  'to your campaign.')

    def test_updates(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-list',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)

        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_goals(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-list',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)

        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_goals_create(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-list',
                      kwargs={'owner_username': self.quest.owner_username})
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
        self.quest.editors.disconnect(self.pleb)
        self.quest.moderators.disconnect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('goal-list',
                      kwargs={'owner_username': self.quest.owner_username})
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
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            'summary': 'This is a test summary',
            'description': 'This is a test description',
            'pledged_vote_requirement': 100,
            'monetary_requirement': 1000
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.data['title'], ['This field is required.'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_create(self):
        self.client.force_authenticate(user=self.user)
        active_round = Round(active=True).save()
        target_goal = Goal(monetary_requirement=1000, target=True,
                           total_required=1000).save()
        active_round.goals.connect(target_goal)
        url = reverse('update-list',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            'content': 'Test Content for Update',
            'title': 'This is a test update'
        }
        response = self.client.post(url, data=data, format='json')
        update = Update.nodes.get(
            object_uuid=Quest.get_updates(self.quest.owner_username)[0])

        self.assertTrue(self.quest.updates.is_connected(update))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_create_invalid(self):
        self.client.force_authenticate(user=self.user)
        target_goal = Goal(monetary_requirement=1000, target=True,
                           total_required=1000).save()
        self.quest.goals.connect(target_goal)
        url = reverse('update-list',
                      kwargs={'owner_username': self.quest.owner_username})
        data = {
            'content': 'Test Content for Update',
            'title': 'too'
        }
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_create_render(self):
        self.client.force_authenticate(user=self.user)
        update = Update(content='test content', title='test title').save()
        self.quest.updates.connect(update)
        url = reverse('update-render',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['results']['html'])

    def test_pledged_votes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-pledged-votes-per-day',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unassigned_goals(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('campaign-unassigned-goals',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_possible_helpers(self):
        self.client.force_authenticate(user=self.user)
        self.quest.owner_username = self.pleb.username
        self.quest.save()
        url = reverse('campaign-possible-helpers',
                      kwargs={'owner_username': self.quest.owner_username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class QuestUpdateTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'updates'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.quest.editors.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        self.pleb.quest.connect(self.quest)
        self.goal = Goal(title="This is my test goal").save()

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('update-list',
                      kwargs={"object_uuid": self.quest.owner_username})
        data = {
            "campaign": self.quest.owner_username,
            "goals": [self.goal.title],
            "title": "This is a test update",
            "content": "I repeat, this is a test update"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        update = Update.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(update.title, data['title'])
        self.assertTrue(self.goal in update.goals)

    def test_create_multiple_goals(self):
        self.client.force_authenticate(user=self.user)
        goal2 = Goal(title='This is another test goal').save()
        url = reverse('update-list',
                      kwargs={"object_uuid": self.quest.owner_username})
        data = {
            "campaign": self.quest.owner_username,
            "goals": [self.goal.title, goal2.title],
            "title": "This is a test update",
            "content": "I repeat, this is a test update"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        update = Update.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(update.title, data['title'])
        self.assertTrue(self.goal in update.goals)
        self.assertTrue(goal2 in update.goals)

    def test_create_three_goals(self):
        self.client.force_authenticate(user=self.user)
        goal2 = Goal(title='This is another test goal').save()
        goal3 = Goal(title='Yet another test goal').save()
        url = reverse('update-list',
                      kwargs={"object_uuid": self.quest.owner_username})
        data = {
            "campaign": self.quest.owner_username,
            "goals": [self.goal.title, goal2.title, goal3.title],
            "title": "This is a test update",
            "content": "I repeat, this is a test update"
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        update = Update.nodes.get(object_uuid=response.data['id'])
        self.assertEqual(update.title, data['title'])
        self.assertTrue(self.goal in update.goals)
        self.assertTrue(goal2 in update.goals)
        self.assertTrue(goal3 in update.goals)


class PositionEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'position'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.pleb.quest.connect(self.quest)
        self.quest.moderators.connect(self.pleb)
        self.quest.editors.connect(self.pleb)
        self.position = Position(name="Senator").save()
        self.position.campaigns.connect(self.quest)
        for item in Location.nodes.all():
            item.delete()
        self.location = Location(name="Michigan").save()
        for camp in self.pleb.campaign.all():
            camp.delete()
        cache.clear()

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

        self.assertEqual(response.data['campaigns'], [])

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

    def test_add_non_admin(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('position-add')
        response = self.client.post(url, {
            "name": "Council Member",
            "location_name": "Michigan",
            "location_uuid": ""
        }, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_add_anon(self):
        url = reverse('position-add')
        response = self.client.post(url, {
            "name": "Council Member",
            "location_name": "Michigan",
            "location_uuid": ""
        }, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_add_admin(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('position-add')
        response = self.client.post(url, {
            "name": "Mayor",
            "location_name": self.location.name,
            "location_uuid": ""
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Mayor')
        self.assertEqual(response.data['location'], self.location.object_uuid)

    def test_add_get(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('position-add')
        response = self.client.get(url)
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_add_uuid(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('position-add')
        response = self.client.post(url, {
            "name": "Governor",
            "location_name": "",
            "location_uuid": self.location.object_uuid
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Governor')

    def test_add_invalid_serializer(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('position-add')
        response = self.client.post(url, {
            "name": "Delegate",
            "location_uuid": self.location.object_uuid
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
