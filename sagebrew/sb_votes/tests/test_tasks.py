import time
from uuid import uuid1
from django.contrib.auth.models import User
from django.test import TestCase
from django.conf import settings

from sb_posts.neo_models import Post
from sb_comments.neo_models import Comment
from sb_base.neo_models import VotableContent
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question

from sb_votes.neo_models import Vote
from sb_votes.tasks import (vote_object_task, object_vote_notifications,
                            create_vote_node)


class TestVoteObjectTask(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_vote_object_task_success_true_vote(self):
        question = Question(object_uuid=str(uuid1()),
                            title=str(uuid1())).save()
        question.owned_by.connect(self.pleb)
        task_data = {
            'object_uuid': question.object_uuid,
            'current_pleb': self.pleb.username,
            'vote_type': True
        }
        res = vote_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, VotableContent)

    def test_vote_object_task_success_false_vote(self):
        question = Question(object_uuid=str(uuid1()),
                            title=str(uuid1())).save()
        question.owned_by.connect(self.pleb)
        task_data = {
            'object_uuid': question.object_uuid,
            'current_pleb': self.pleb.username,
            'vote_type': False
        }
        res = vote_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, VotableContent)

    def test_vote_object_task_success_2_vote(self):
        question = Question(object_uuid=str(uuid1()),
                            title=str(uuid1())).save()
        question.owned_by.connect(self.pleb)
        task_data = {
            'object_uuid': question.object_uuid,
            'current_pleb': self.pleb.username,
            'vote_type': 2
        }
        res = vote_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, VotableContent)

    def test_vote_object_task_previous_vote_exists(self):
        question = Question(object_uuid=str(uuid1()),
                            title=str(uuid1())).save()
        question.owned_by.connect(self.pleb)
        vote = Vote(vote_type=0).save()
        vote.owned_by.connect(self.pleb)
        question.last_votes.connect(vote)
        vote.vote_on.connect(question)
        task_data = {
            'object_uuid': question.object_uuid,
            'current_pleb': self.pleb.username,
            'vote_type': True
        }
        res = vote_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, VotableContent)

    def test_vote_object_task_pleb_does_not_exist(self):
        question = Question(object_uuid=str(uuid1()),
                            title=str(uuid1())).save()
        question.owned_by.connect(self.pleb)
        task_data = {
            'object_uuid': question.object_uuid,
            'current_pleb': str(uuid1()),
            'vote_type': True
        }
        res = vote_object_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Exception)


class TestObjectVoteNotifications(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(owner_username=self.pleb.username,
                                 title=str(uuid1())).save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_initial_vote_create(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": None,
            "new_vote_type": 1,
            "voting_pleb": self.pleb.username
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)

    def test_change_vote_down_to_up(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": 0,
            "new_vote_type": 1,
            "voting_pleb": self.pleb.username
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)

    def test_change_vote_up_to_down(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": 1,
            "new_vote_type": 0,
            "voting_pleb": self.pleb.username
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)

    def test_pos_rep_change(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": 0,
            "new_vote_type": 1,
            "voting_pleb": self.pleb.username
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)

    def test_neg_rep_change(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": 1,
            "new_vote_type": 0,
            "voting_pleb": self.pleb.username
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)

    def test_pleb_does_not_exist(self):
        data = {
            "object_uuid": self.question.object_uuid,
            "previous_vote_type": 1,
            "new_vote_type": 0,
            "voting_pleb": str(uuid1())
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Exception)

    def test_initial_vote_create_private_content(self):
        post = Post(content='test content').save()
        data = {
            "object_uuid": post.object_uuid,
            "previous_vote_type": None,
            "new_vote_type": 1,
            "voting_pleb": self.pleb.username
        }

        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)

    def test_initial_vote_create_private_comment(self):
        post = Post().save()
        comment = Comment(content='test content', visibility="private").save()
        post.comments.connect(comment)
        data = {
            "object_uuid": comment.object_uuid,
            "previous_vote_type": None,
            "new_vote_type": 1,
            "voting_pleb": self.pleb.username
        }
        res = object_vote_notifications.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        self.assertNotIsInstance(res.result, Exception)


class TestCreateVoteNodeTask(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question(owner_username=self.pleb.username,
                                 title=str(uuid1())).save()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_vote_node(self):
        question = Question(object_uuid=str(uuid1()),
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        task_data = {
            'node_id': str(uuid1()),
            'voter': self.pleb.username,
            'parent_object': question.object_uuid,
            'vote_type': 1
        }
        res = create_vote_node.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        test_vote = Vote.nodes.get(object_uuid=task_data['node_id'])
        self.assertEqual(test_vote.reputation_change, 5)
        self.assertTrue(question.first_votes.is_connected(test_vote))
        self.assertTrue(question.last_votes.is_connected(test_vote))

    def test_create_vote_node_false(self):
        question = Question(object_uuid=str(uuid1()),
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        task_data = {
            'node_id': str(uuid1()),
            'voter': self.pleb.username,
            'parent_object': question.object_uuid,
            'vote_type': 0
        }
        res = create_vote_node.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        test_vote = Vote.nodes.get(object_uuid=task_data['node_id'])
        self.assertEqual(test_vote.reputation_change, -2)
        self.assertTrue(question.first_votes.is_connected(test_vote))
        self.assertTrue(question.last_votes.is_connected(test_vote))

    def test_multiple_votes(self):
        vote = Vote(vote_type=0, reputation_change=-2).save()
        question = Question(object_uuid=str(uuid1()),
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        question.last_votes.connect(vote)
        question.first_votes.connect(vote)
        vote.vote_on.connect(question)
        vote.owned_by.connect(self.pleb)
        task_data = {
            'node_id': str(uuid1()),
            'voter': self.pleb.username,
            'parent_object': question.object_uuid,
            'vote_type': 1
        }
        res = create_vote_node.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        test_vote = Vote.nodes.get(object_uuid=task_data['node_id'])
        self.assertEqual(test_vote.reputation_change, 5)
        self.assertTrue(question.first_votes.is_connected(vote))
        self.assertFalse(question.last_votes.is_connected(vote))
        self.assertTrue(question.last_votes.is_connected(test_vote))

    def test_vote_private(self):
        post = Post(object_uuid=str(uuid1()),
                    owner_username=self.pleb.username).save()
        post.owned_by.connect(self.pleb)
        task_data = {
            'node_id': str(uuid1()),
            'voter': self.pleb.username,
            'parent_object': post.object_uuid,
            'vote_type': 0
        }
        res = create_vote_node.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        test_vote = Vote.nodes.get(object_uuid=task_data['node_id'])
        self.assertEqual(test_vote.reputation_change, 0)
        self.assertTrue(post.first_votes.is_connected(test_vote))
        self.assertTrue(post.last_votes.is_connected(test_vote))

    def test_pleb_does_not_exist(self):
        question = Question(object_uuid=str(uuid1()),
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        task_data = {
            'node_id': str(uuid1()),
            'voter': str(uuid1()),
            'parent_object': question.object_uuid,
            'vote_type': 1
        }
        res = create_vote_node.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, Exception)

    def test_owner_does_not_exist(self):
        question = Question(object_uuid=str(uuid1()),
                            title=str(uuid1()),
                            owner_username=str(uuid1())).save()
        question.owned_by.connect(self.pleb)
        task_data = {
            'node_id': str(uuid1()),
            'voter': self.pleb.username,
            'parent_object': question.object_uuid,
            'vote_type': 1
        }
        res = create_vote_node.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, Exception)
