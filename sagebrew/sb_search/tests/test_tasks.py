import time
from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from plebs.neo_models import Pleb
from sb_posts.neo_models import SBPost
from sb_answers.neo_models import SBAnswer
from sb_questions.neo_models import SBQuestion
from sb_search.tasks import update_weight_relationship

class TestUpdateWeightRelationshipTaskQuestion(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.question = SBQuestion(question_id=str(uuid1()))
        self.question.save()

    def tearDown(self):
        call_command('clear_neo_db')

    def test_update_weight_relationship_task_success_seen_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'search_seen'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_comment_on_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'comment_on'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_flag_as_inappropriate_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_inappropriate'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_flag_as_spam_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_spam'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_share_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'share'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 150)

    def test_update_weight_relationship_task_success_answered_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'answered'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)

    def test_update_weight_relationship_task_success_seen_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'search_seen'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 155)

    def test_update_weight_relationship_task_success_comment_on_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'comment_on'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 155)

    def test_update_weight_relationship_task_success_flag_as_inappropriate_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_inappropriate'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 145)

    def test_update_weight_relationship_task_success_flag_as_spam_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_spam'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 50)

    def test_update_weight_relationship_task_success_share_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'share'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 157)

    def test_update_weight_relationship_task_success_answered_connected(self):
        res = self.pleb.obj_weight_connect(self.question)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'question',
                'object_uuid': self.question.question_id,
                'current_pleb': self.user.email,
                'modifier_type': 'answered'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.question.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.question))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.question).weight, 200)

class TestUpdateWeightRelationshipTaskAnswer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.answer = SBAnswer(answer_id=str(uuid1()))
        self.answer.save()

    def tearDown(self):
        call_command('clear_neo_db')

    def test_update_weight_relationship_task_success_seen_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'search_seen'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 150)

    def test_update_weight_relationship_task_success_comment_on_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'comment_on'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 150)

    def test_update_weight_relationship_task_success_flag_as_inappropriate_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_inappropriate'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 150)

    def test_update_weight_relationship_task_success_flag_as_spam_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_spam'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 150)

    def test_update_weight_relationship_task_success_share_unconnected(self):
        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'share'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)

        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 150)

    def test_update_weight_relationship_task_success_seen_connected(self):
        res = self.pleb.obj_weight_connect(self.answer)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'search_seen'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 155)

    def test_update_weight_relationship_task_success_comment_on_connected(self):
        res = self.pleb.obj_weight_connect(self.answer)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'comment_on'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 155)

    def test_update_weight_relationship_task_success_flag_as_inappropriate_connected(self):
        res = self.pleb.obj_weight_connect(self.answer)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_inappropriate'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 145)

    def test_update_weight_relationship_task_success_flag_as_spam_connected(self):
        res = self.pleb.obj_weight_connect(self.answer)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'flag_as_spam'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 50)

    def test_update_weight_relationship_task_success_share_connected(self):
        res = self.pleb.obj_weight_connect(self.answer)

        self.assertIsNot(res, False)

        data = {"document_id": str(uuid1()),
                'index': 'full-search-user-specific-1',
                'object_type': 'answer',
                'object_uuid': self.answer.answer_id,
                'current_pleb': self.user.email,
                'modifier_type': 'share'}
        res = update_weight_relationship.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.pleb.refresh()
        self.answer.refresh()

        self.assertTrue(self.pleb.obj_weight_is_connected(self.answer))
        self.assertTrue(res)
        self.assertEqual(self.pleb.obj_weight_relationship(self.answer).weight, 157)

class TestUpdateWeightRelationshipTaskPleb(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb1 = Pleb.nodes.get(email=self.user1.email)
        self.user2 = User.objects.create_user(
            username='Tyler2', email=str(uuid1())+'@gmail.com')
        self.pleb2 = Pleb.nodes.get(email=self.user2.email)

    def tearDown(self):
        call_command('clear_neo_db')

class TestUpdateWeightRelationshipTaskPost(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb1 = Pleb.nodes.get(email=self.user1.email)
        self.user2 = User.objects.create_user(
            username='Tyler2', email=str(uuid1())+'@gmail.com')
        self.pleb2 = Pleb.nodes.get(email=self.user2.email)

    def tearDown(self):
        call_command('clear_neo_db')

