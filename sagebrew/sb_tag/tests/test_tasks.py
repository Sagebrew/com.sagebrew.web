import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from sb_questions.neo_models import SBQuestion
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util

from sb_tag.neo_models import SBAutoTag
from sb_tag.tasks import add_auto_tags, add_tags, create_tag_relations


class TestTagTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_tag_success(self):
        question = SBQuestion(sb_id=uuid1())
        question.save()
        tags = ['test','tag','please','do', 'not','fail','in', 'testing']
        task_dict = {'question': question,
                     'tags': tags}
        res = add_tags.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)


class TestAutoTagTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_auto_tag_success(self):
        question = SBQuestion(sb_id=uuid1())
        question.save()
        task_dict = {
            'question': question,
            'tag_list': [{'tags': {'relevance': '.9','text': 'test'}}]
        }
        res = add_auto_tags.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)


class TestCreateAutoTagRelationships(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_auto_tag_relationship_success(self):
        tag_list = []
        for item in range(0,9):
            tag = SBAutoTag(tag_name='test_tag'+str(uuid1()))
            tag.save()
            tag_list.append(tag)
        res = create_tag_relations.apply_async(kwargs={"tag_list": tag_list})
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

    def test_create_auto_tag_relaitonship_fequently_tagged_with(self):
        tag1 = SBAutoTag(tag_name=str(uuid1())).save()
        tag2 = SBAutoTag(tag_name=str(uuid1())).save()
        rel = tag1.frequently_auto_tagged_with.connect(tag2)
        rel.save()
        rel2 = tag2.frequently_auto_tagged_with.connect(tag1)
        rel2.save()
        tag_list = [tag1, tag2]
        res = create_tag_relations.apply_async(kwargs={"tag_list": tag_list})
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)

    def test_create_auto_tag_relationship_empty_list(self):
        res = create_tag_relations.apply_async(kwargs={"tag_list": []})
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertIsInstance(res, TypeError)
