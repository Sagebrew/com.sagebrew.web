from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_flags.neo_models import Flag
from sb_questions.neo_models import Question

from sb_council.utils import update_closed, check_closed_reputation_changes


class TestUpdateClosed(TestCase):
    def setUp(self):
        self.unit_under_test_name = 'sbcontent'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.flag = Flag().save()
        self.question = Question(owner_username=self.pleb.username,
                                 title=str(uuid1())).save()
        self.question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(self.question)
        self.question.flags.connect(self.flag)
        self.vote_rel = self.question.council_votes.connect(self.pleb)
        self.vote_rel.active = True
        self.vote_rel.vote_type = True
        self.vote_rel.save()

    def test_update_closed(self):
        res = update_closed(self.question.object_uuid)

        self.assertTrue(res)
        self.question.refresh()

        self.assertTrue(self.question.is_closed)

    def test_update_closed_to_open(self):
        self.vote_rel.vote_type = False
        self.vote_rel.save()

        res = update_closed(self.question.object_uuid)
        self.assertTrue(res)
        self.question.refresh()

        self.assertFalse(self.question.is_closed)

    def test_update_closed_inactive(self):
        self.vote_rel.active = False
        self.vote_rel.save()

        res = update_closed(self.question.object_uuid)
        self.assertTrue(res)
        self.question.refresh()

        self.assertFalse(self.question.is_closed)


class TestCheckClosedReputationChanges(TestCase):
    def setUp(self):
        self.unit_under_test_name = 'sbcontent'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.flag = Flag().save()
        self.question = Question(owner_username=self.pleb.username,
                                 title=str(uuid1())).save()
        self.question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(self.question)
        self.question.flags.connect(self.flag)
        self.vote_rel = self.question.council_votes.connect(self.pleb)
        self.vote_rel.active = True
        self.vote_rel.vote_type = True
        self.vote_rel.save()

    def test_check_closed_reputation_changes(self):
        res = check_closed_reputation_changes()
        self.assertTrue(res)
