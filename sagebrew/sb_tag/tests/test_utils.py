from uuid import uuid1
from django.contrib.auth.models import User
from django.test import TestCase

from api.utils import test_wait_util
from sb_questions.neo_models import SBQuestion
from sb_tag.utils import (add_tag_util, add_auto_tags_util,
                          create_tag_relations)
from sb_tag.neo_models import SBAutoTag
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util


class TestCreateTagUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_create_tag_util_success(self):
        question = SBQuestion(sb_id=uuid1())
        question.save()
        tags = ['test','tag','please','do', 'not','fail','in', 'testing']
        res = add_tag_util(object_type='question',
                           object_uuid=question.sb_id,
                           tags=tags)

        self.assertTrue(res)

    def test_create_tag_util_object_does_not_exist(self):
        tags = ['test','tag','please','do', 'not','fail','in', 'testing']
        res = add_tag_util(object_type='question',
                           object_uuid=uuid1(),
                           tags=tags)

        self.assertFalse(res)

    def test_create_tag_util_invalid_object(self):
        question = SBQuestion(sb_id=uuid1())
        question.save()
        tags = ['test','tag','please','do', 'not','fail','in', 'testing']
        res = add_tag_util(object_type='nothing',
                           object_uuid=question.sb_id,
                           tags=tags)

        self.assertFalse(res)

    def test_create_tag_util_empty_tags(self):
        question = SBQuestion(sb_id=uuid1())
        question.save()
        tags = []
        res = add_tag_util(object_type='question',
                           object_uuid=question.sb_id,
                           tags=tags)

        self.assertFalse(res)

class TestCreateAutoTagUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_create_auto_tag_util_success(self):
        question = SBQuestion(sb_id=str(uuid1()))
        question.save()
        util_dict = [{'object_type': 'question',
                      'object_uuid': question.sb_id,
                      'tags': {'relevance': '.9', 'text': 'test auto tag'}}]
        res = add_auto_tags_util(util_dict)

        self.assertTrue(res)

    def test_create_auto_tag_util_success_tag_exists(self):
        sb_id = uuid1()
        question = SBQuestion(sb_id=sb_id)
        question.save()
        util_dict = [{'object_type': 'question',
                      'object_uuid': sb_id,
                      'tags': {'relevance': '.9', 'text': 'test auto tag'}},
                     {'object_type': 'question',
                      'object_uuid': sb_id,
                      'tags': {'relevance': '.9', 'text': 'test fake tag'}},
                     {'object_type': 'question',
                      'object_uuid': sb_id,
                      'tags': {'relevance': '.9', 'text': 'test auto tag'}}]
        res = add_auto_tags_util(util_dict)

        self.assertTrue(res)

    def test_create_auto_tag_util_object_does_not_exist(self):
        util_dict = [{'object_type': 'question',
                      'object_uuid': uuid1(),
                      'tags': {'relevance': '.9', 'text': 'test'}}]

        res = add_auto_tags_util(util_dict)

        self.assertFalse(res)

    def test_create_auto_tag_util_invalid_object(self):
        question = SBQuestion(sb_id=uuid1())
        question.save()
        util_dict = [{'object_type': 'nothing',
                      'object_uuid': question.sb_id,
                      'tags': {'relevance': '.9', 'text': 'test'}}]
        res = add_auto_tags_util(util_dict)

        self.assertFalse(res)

    def test_create_auto_tag_key_error(self):
        question = SBQuestion(sb_id=uuid1())
        question.save()
        util_dict = [{'object_type': 'nothing',
                      'object_uuid': question.sb_id}]
        res = add_auto_tags_util(util_dict)

        self.assertFalse(res)

class TestCreateAutoTagRelationships(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_create_auto_tag_relationship_success(self):
        tag_list = []
        for item in range(0,9):
            tag = SBAutoTag(tag_name='test_tag'+str(uuid1()))
            tag.save()
            tag_list.append(tag)
        res = create_tag_relations(tag_list)

        self.assertTrue(res)

    def test_create_auto_tag_relaitonship_fequently_tagged_with(self):
        tag1 = SBAutoTag(tag_name=str(uuid1())).save()
        tag2 = SBAutoTag(tag_name=str(uuid1())).save()
        rel = tag1.frequently_auto_tagged_with.connect(tag2)
        rel.save()
        rel2 = tag2.frequently_auto_tagged_with.connect(tag1)
        rel2.save()
        tag_list = [tag1, tag2]
        res = create_tag_relations(tag_list)
        self.assertTrue(res)

    def test_create_auto_tag_relationship_empty_list(self):
        res = create_tag_relations([])

        self.assertFalse(res)
