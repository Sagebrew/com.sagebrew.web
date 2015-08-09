from django.test.testcases import TestCase
from django.contrib.auth.models import User

from sb_comments.neo_models import Comment
from sb_questions.neo_models import Question
from sb_registration.utils import create_user_util_test

from plebs.neo_models import BetaUser, Pleb


class TestBetaUser(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_beta_user_invite(self):
        beta_user = BetaUser(email="thisistotallyanemail").save()
        res = beta_user.invite()
        self.assertTrue(res)


class TestPleb(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_update_campaign(self):
        self.assertTrue(self.pleb.update_campaign())

    def test_get_official_phone(self):
        self.assertIsNone(self.pleb.get_official_phone())

    def test_get_badges(self):
        self.assertIsNotNone(self.pleb.get_badges())

    def test_get_full_name(self):
        self.assertEqual(self.pleb.get_full_name(), "test test")

    def test_relate_comment(self):
        comment = Comment().save()
        self.assertTrue(self.pleb.relate_comment(comment))

    def test_update_weight_relationship(self):
        sb_object = Question().save()
        rel = self.pleb.object_weight.connect(sb_object)
        rel.weight = 0
        rel.save()
        res = self.pleb.update_weight_relationship(sb_object, 'seen_search')
        self.assertEqual(res, 5)

    def test_get_question_count(self):
        self.assertEqual(0, self.pleb.get_question_count())

    def test_get_solution_count(self):
        self.assertEqual(0, self.pleb.get_solution_count())

    def test_get_post_count(self):
        self.assertEqual(0, self.pleb.get_post_count())

    def test_get_comment_count(self):
        self.assertEqual(0, self.pleb.get_comment_count())

    def test_get_friends(self):
        self.assertIsNotNone(self.pleb.get_friends())
