import pytz
import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from plebs.neo_models import Pleb
from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test
from sb_docstore.utils import add_object_to_table

from sb_votes.utils import (determine_update_values, determine_vote_type,
                            handle_vote)


class TestDetermineUpdateValues(TestCase):
    def setUp(self):
        self.tags = []
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_determine_update_values_no_effect(self):
        upvote, downvote = determine_update_values(1, 1, 1, 0)

        self.assertEqual(upvote, 1)
        self.assertEqual(downvote, 0)

    def test_determine_update_value_upvote_to_none(self):
        upvote, downvote = determine_update_values(1, 2, 1, 0)

        self.assertEqual(upvote, 0)
        self.assertEqual(downvote, 0)

    def test_determine_update_value_upvote_to_downvote(self):
        upvote, downvote = determine_update_values(1, 0, 1, 0)

        self.assertEqual(upvote, 0)
        self.assertEqual(downvote, 1)

    def test_determine_update_values_down_to_down(self):
        upvote, downvote = determine_update_values(0, 0, 0, 1)

        self.assertEqual(upvote, 0)
        self.assertEqual(downvote, 1)

    def test_determine_update_values_down_to_none(self):
        upvote, downvote = determine_update_values(0, 2, 0, 1)

        self.assertEqual(upvote, 0)
        self.assertEqual(downvote, 0)

    def test_determine_update_values_down_to_up(self):
        upvote, downvote = determine_update_values(0, 1, 0, 1)

        self.assertEqual(upvote, 1)
        self.assertEqual(downvote, 0)

    def test_determine_update_values_none_to_up(self):
        upvote, downvote = determine_update_values(2, 1, 0, 0)

        self.assertEqual(upvote, 1)
        self.assertEqual(downvote, 0)

    def test_determine_update_values_none_to_down(self):
        upvote, downvote = determine_update_values(2, 0, 0, 0)

        self.assertEqual(upvote, 0)
        self.assertEqual(downvote, 1)


class TestDetermineVoteType(TestCase):
    def setUp(self):
        self.tags = []
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question().save()

    def test_handle_vote_without_vote(self):
        res = determine_vote_type(self.question.object_uuid,
                                  self.pleb.username)
        self.assertIsNone(res)

    def test_determine_vote_type_with_vote(self):
        vote_data = {
            "status": 1,
            "parent_object": self.question.object_uuid,
            "user": self.pleb.username
        }
        res1 = add_object_to_table("votes", vote_data)
        self.assertTrue(res1)
        res2 = determine_vote_type(self.question.object_uuid,
                                   self.pleb.username)
        self.assertTrue(res2)

    def test_determine_vote_type_with_vote_none(self):
        vote_data = {
            "status": 2,
            "parent_object": self.question.object_uuid,
            "user": self.pleb.username
        }
        res1 = add_object_to_table("votes", vote_data)
        self.assertTrue(res1)
        res2 = determine_vote_type(self.question.object_uuid,
                                   self.pleb.username)
        self.assertIsNone(res2)


class TestHandleVote(TestCase):
    def setUp(self):
        self.tags = []
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question = Question().save()

    def test_handle_vote_no_vote(self):
        res = handle_vote(self.question.object_uuid, 1, self.user.username,
                          str(datetime.datetime.now(pytz.utc)))
        self.assertTrue(res)

    def test_handle_vote_already_voted(self):
        vote_data = {
            "status": 1,
            "parent_object": self.question.object_uuid,
            "user": self.pleb.username
        }
        res1 = add_object_to_table("votes", vote_data)
        self.assertTrue(res1)
        res = handle_vote(self.question.object_uuid, 1, self.user.username,
                          str(datetime.datetime.now(pytz.utc)))
        self.assertTrue(res)
