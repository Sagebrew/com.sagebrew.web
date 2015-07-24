from django.contrib.auth.models import User
from django.test import TestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

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
        