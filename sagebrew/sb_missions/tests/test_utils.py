import copy
from uuid import uuid1

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache

from neomodel import db

from sagebrew.sb_quests.neo_models import Quest
from sagebrew.sb_registration.utils import create_user_util_test
from sagebrew.sb_missions.neo_models import Mission
from sagebrew.sb_missions.utils import setup_onboarding, order_tasks


class TestSetupOnboarding(TestCase):
    def setUp(self):
        query = 'MATCH (a) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)

        self.email = "success@simulator.amazonses.com"
        self.password = "test_test"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()
        cache.clear()
        self.mission = Mission(owner_username=self.user.username,
                               title=str(uuid1())).save()
        self.quest = Quest(owner_username=self.pleb.username).save()
        self.quest.missions.connect(self.mission)
        self.quest.owner.connect(self.pleb)

    def test_verify_same_onboarding_task_list(self):
        temp_list = copy.deepcopy(settings.ONBOARDING_TASKS)
        setup_onboarding(self.quest, self.mission)
        self.assertEqual(temp_list, settings.ONBOARDING_TASKS)

    def test_set_wallpaper(self):
        self.quest.wallpaper_pic = "something.png"
        self.quest.save()
        setup_onboarding(self.quest, self.mission)
        query = 'MATCH (a:Mission {object_uuid: "%s"})-[:MUST_COMPLETE]->' \
                '(task:OnboardingTask {title: "%s"}) RETURN task' % (
                    self.mission.object_uuid, settings.QUEST_WALLPAPER_TITLE)
        res, _ = db.cypher_query(query)
        self.assertTrue(res[0][0]['completed'])

    def test_set_bank_setup(self):
        self.quest.account_verified = "verified"
        self.quest.save()
        setup_onboarding(self.quest, self.mission)
        query = 'MATCH (a:Mission {object_uuid: "%s"})-[:MUST_COMPLETE]->' \
                '(task:OnboardingTask {title: "%s"}) RETURN task' % (
                    self.mission.object_uuid, settings.BANK_SETUP_TITLE)
        res, _ = db.cypher_query(query)
        self.assertTrue(res[0][0]['completed'])

    def test_set_quest_about(self):
        self.quest.about = "some short summary"
        self.quest.save()
        setup_onboarding(self.quest, self.mission)
        query = 'MATCH (a:Mission {object_uuid: "%s"})-[:MUST_COMPLETE]->' \
                '(task:OnboardingTask {title: "%s"}) RETURN task' % (
                    self.mission.object_uuid, settings.QUEST_ABOUT_TITLE)
        res, _ = db.cypher_query(query)
        self.assertTrue(res[0][0]['completed'])


class TestOrderTasks(TestCase):
    def setUp(self):
        query = 'MATCH (a) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        self.email = "success@simulator.amazonses.com"
        self.password = "test_test"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.email_verified = True
        self.pleb.save()
        cache.clear()
        self.mission = Mission(owner_username=self.user.username,
                               title=str(uuid1())).save()
        self.quest = Quest(owner_username=self.pleb.username).save()
        self.quest.missions.connect(self.mission)
        self.quest.owner.connect(self.pleb)

    def test_uncompleted_sort(self):
        setup_onboarding(self.quest, self.mission)
        db.cypher_query('MATCH (a:OnboardingTask {title: "Mission Setup"}) '
                        'SET a.completed=False RETURN a')
        uncompleted_sort, completed_count = order_tasks(
            self.mission.object_uuid)
        self.assertEqual(len(uncompleted_sort), len(settings.ONBOARDING_TASKS))
        for item in range(0, len(settings.ONBOARDING_TASKS) - 1):
            self.assertEqual(uncompleted_sort[item]['priority'], item + 1)

    def test_completed_sort_none_completed(self):
        setup_onboarding(self.quest, self.mission)
        db.cypher_query('MATCH (a:OnboardingTask {title: "Mission Setup"}) '
                        'SET a.completed=False RETURN a')
        uncompleted_sort, completed_count = order_tasks(
            self.mission.object_uuid)
        self.assertEqual(completed_count, 0)

    def test_completed_sort_one_completed(self):
        self.quest.account_verified = "verified"
        self.quest.save()
        setup_onboarding(self.quest, self.mission)
        db.cypher_query('MATCH (a:OnboardingTask {title: "Mission Setup"}) '
                        'SET a.completed=False RETURN a')
        uncompleted_sort, completed_count = order_tasks(
            self.mission.object_uuid)
        self.assertEqual(completed_count, 1)
        self.assertTrue(
            uncompleted_sort[len(uncompleted_sort) - 1]['completed'])
