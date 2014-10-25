import time
from django.conf import settings
from django.test.testcases import TestCase

from govtrack.tasks import (populate_gt_role, populate_gt_person,
                            populate_gt_votes, populate_gt_committee)

class TestPopulateGTRoleTask(TestCase):
    def setUp(self):
        self.role_url = 'https://www.govtrack.us/api/v2/role'
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_gt_role_success(self):
        res = populate_gt_role.apply_async(args=[self.role_url])
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)


class TestPopulateGTPersonTask(TestCase):
    def setUp(self):
        self.person_url = 'https://www.govtrack.us/api/v2/person'
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_gt_person_success(self):
        res = populate_gt_person.apply_async(args=[self.person_url])
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)


class TestPopulateGTCommitteeTask(TestCase):
    def setUp(self):
        self.committee_url = 'https://www.govtrack.us/api/v2/committee'
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_gt_committee_success(self):
        res = populate_gt_committee.apply_async(args=[self.committee_url])
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)

class TestPopulateGTVotesTask(TestCase):
    def setUp(self):
        self.vote_url = 'https://www.govtrack.us/api/v2/vote'
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_gt_vote_success(self):
        res = populate_gt_votes.apply_async(args=[self.vote_url])
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)