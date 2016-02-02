# import time
from uuid import uuid1

from django.test.testcases import TestCase
from django.contrib.auth.models import User
# from django.core.cache import cache

from neomodel import DoesNotExist, MultipleNodesReturned, db

# from sb_votes.neo_models import Vote
from sb_comments.neo_models import Comment
from sb_donations.neo_models import Donation
from sb_questions.neo_models import Question
from sb_locations.neo_models import Location
from sb_registration.utils import create_user_util_test

from plebs.neo_models import BetaUser, Pleb, Address


class TestBetaUser(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
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
        res = create_user_util_test(self.email, task=True)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_update_quest(self):
        self.assertTrue(self.pleb.update_quest())

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
        sb_object = Question(title="Hello I'm testing weights on my "
                                   "question!").save()
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

    def test_get_donations(self):
        donation = Donation().save()
        self.pleb.donations.connect(donation)
        donation.owned_by.connect(self.pleb)
        self.assertFalse(self.pleb.get_donations())

    def test_get_sagebrew_donations(self):
        donation = Donation().save()
        self.pleb.donations.connect(donation)
        donation.owned_by.connect(self.pleb)
        self.assertTrue(self.pleb.get_sagebrew_donations())

    def test_is_following(self):
        test_pleb = Pleb(username=str(uuid1())).save()
        rel = self.pleb.following.connect(test_pleb)
        rel.save()
        res = test_pleb.is_following(self.pleb.username)
        self.assertTrue(res)

    def test_is_following_not_following(self):
        test_pleb = Pleb(username=str(uuid1())).save()
        res = test_pleb.is_following(self.pleb.username)
        self.assertFalse(res)

    def test_is_following_was_following(self):
        test_pleb = Pleb(username=str(uuid1())).save()
        rel = self.pleb.following.connect(test_pleb)
        rel.active = False
        rel.save()
        res = test_pleb.is_following(self.pleb.username)
        self.assertFalse(res)

    def test_follow(self):
        test_pleb = Pleb(username=str(uuid1())).save()
        res = test_pleb.follow(self.pleb.username)
        self.assertTrue(res)
        self.assertTrue(test_pleb.is_following(self.pleb.username))

    def test_unfollow(self):
        test_pleb = Pleb(username=str(uuid1())).save()
        res = test_pleb.unfollow(self.pleb.username)
        self.assertFalse(res)


class TestPlebReputationChange(TestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

'''
    def test_get_reputation_change_over_time(self):
        cache.clear()
        comment = Comment(content="some arbitrary test comment",
                          owner_username=self.pleb.username).save()
        comment.owned_by.connect(self.pleb)
        self.pleb.comments.connect(comment)
        old_vote = Vote(vote_type=1, reputation_change=5).save()
        self.pleb.last_counted_vote_node = old_vote.object_uuid
        self.pleb.save()
        time.sleep(1)  # ensure vote gets connected to later second
        vote = Vote(vote_type=1, reputation_change=2).save()
        comment.last_votes.connect(vote)
        comment.first_votes.connect(vote)
        vote.vote_on.connect(comment)
        res = self.pleb.reputation_change
        self.assertEqual(res, 2)

    def test_get_reputation_change_no_change(self):
        cache.clear()
        comment = Comment(content="some arbitrary test comment",
                          owner_username=self.pleb.username).save()
        comment.owned_by.connect(self.pleb)
        self.pleb.comments.connect(comment)
        old_vote = Vote(vote_type=1, reputation_change=5).save()
        self.pleb.last_counted_vote_node = old_vote.object_uuid
        self.pleb.save()
        time.sleep(1)  # ensure vote gets connected to later second
        res = self.pleb.reputation_change
        self.assertEqual(res, 0)

    def test_reputation_change_over_1000(self):
        cache.clear()
        comment = Comment(content="some arbitrary test comment",
                          owner_username=self.pleb.username).save()
        comment.owned_by.connect(self.pleb)
        self.pleb.comments.connect(comment)
        old_vote = Vote(vote_type=1, reputation_change=5).save()
        self.pleb.last_counted_vote_node = old_vote.object_uuid
        self.pleb.save()
        time.sleep(1)  # ensure vote gets connected to later second
        vote = Vote(vote_type=1, reputation_change=1001).save()
        comment.last_votes.connect(vote)
        comment.first_votes.connect(vote)
        vote.vote_on.connect(comment)
        res = self.pleb.reputation_change
        self.assertEqual(res, "1k")

    def test_reputation_change_under_1000(self):
        cache.clear()
        comment = Comment(content="some arbitrary test comment",
                          owner_username=self.pleb.username).save()
        comment.owned_by.connect(self.pleb)
        self.pleb.comments.connect(comment)
        old_vote = Vote(vote_type=1, reputation_change=5).save()
        self.pleb.last_counted_vote_node = old_vote.object_uuid
        self.pleb.save()
        time.sleep(1)  # ensure vote gets connected to later second
        vote = Vote(vote_type=1, reputation_change=-1001).save()
        comment.last_votes.connect(vote)
        comment.first_votes.connect(vote)
        vote.vote_on.connect(comment)
        res = self.pleb.reputation_change
        self.assertEqual(res, "-1k")

    def test_reputation_change_no_nodes(self):
        cache.clear()
        for vote in Vote.nodes.all():
            vote.delete()
        res = self.pleb.reputation_change
        self.assertEqual(res, 0)

    def test_reputation_change_under_1000_cache(self):
        cache.clear()
        comment = Comment(content="some arbitrary test comment",
                          owner_username=self.pleb.username).save()
        comment.owned_by.connect(self.pleb)
        self.pleb.comments.connect(comment)
        old_vote = Vote(vote_type=1, reputation_change=5).save()
        self.pleb.last_counted_vote_node = old_vote.object_uuid
        self.pleb.save()
        time.sleep(1)  # ensure vote gets connected to later second
        vote = Vote(vote_type=1, reputation_change=-1001).save()
        comment.last_votes.connect(vote)
        comment.first_votes.connect(vote)
        vote.vote_on.connect(comment)
        res = self.pleb.reputation_change
        self.assertEqual(res, "-1k")
        res = self.pleb.reputation_change
        self.assertEqual(res, "-1k")
        self.assertEqual(cache.get(
            '%s_reputation_change' % self.pleb.username)['rep_change'], -1001)
'''


class TestAddress(TestCase):

    def setUp(self):
        self.address = Address(city="Wixom", state="MI").save()
        try:
            Location.nodes.get(name="Wixom").delete()
        except (Location.DoesNotExist, DoesNotExist):
            pass
        except MultipleNodesReturned:
            query = 'MATCH (a:Location {name:"Wixom"}) RETURN a'
            res, _ = db.cypher_query(query)
            for location in res[0]:
                Location.inflate(location).delete()
        try:
            self.state = Location.nodes.get(name="Michigan")
        except MultipleNodesReturned:
            query = 'MATCH (a:Location {name:"Michigan"}) RETURN a'
            res, _ = db.cypher_query(query)
            for location in res[0]:
                Location.inflate(location).delete()
        except (Location.DoesNotExist, DoesNotExist):
            self.state = Location(name="Michigan").save()

    def test_set_encompassing_no_nodes(self):
        res = self.address.set_encompassing()
        city = Location.nodes.get(name="Wixom")
        self.assertTrue(res.encompassed_by.is_connected(city))
        city.delete()

    def test_set_encompassing_city_exists(self):
        city = Location(name="Wixom").save()
        city.encompassed_by.connect(self.state)
        self.state.encompasses.connect(city)
        res = self.address.set_encompassing()
        self.assertTrue(res.encompassed_by.is_connected(city))
        city.delete()

    def test_multiple_cities_same_name(self):
        address = Address(city="Redford", state="Michigan").save()
        city = Location(name="Redford").save()
        city2 = Location(name="Redford").save()
        try:
            new_state = Location.nodes.get(name="Washington")
        except (Location.DoesNotExist, DoesNotExist):
            new_state = Location(name="Washington").save()
        self.state.encompasses.connect(city)
        city.encompassed_by.connect(self.state)
        city2.encompassed_by.connect(new_state)

        new_state.encompasses.connect(city2)
        res = address.set_encompassing()
        self.assertTrue(res.encompassed_by.is_connected(city))
        city.delete()
        city2.delete()
        address.delete()
