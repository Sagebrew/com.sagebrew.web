import time

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_campaigns.neo_models import PoliticalCampaign

from sb_goals.tasks import check_goal_completion_task
from sb_goals.neo_models import Round, Goal


class TestCreatePlebTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.username = res["username"]
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        self.round = Round().save()
        self.goal = Goal(total_required=0, pledges_required=0).save()
        self.round.goals.connect(self.goal)
        self.goal.associated_round.connect(self.round)
        self.campaign = PoliticalCampaign().save()
        self.upcoming_round = Round().save()
        self.upcoming_round.campaign.connect(self.campaign)
        self.campaign.upcoming_round.connect(self.upcoming_round)
        self.round.campaign.connect(self.campaign)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_check_goal_completion_task(self):
        data = {
            "round_uuid": self.round.object_uuid
        }
        res = check_goal_completion_task.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertNotIsInstance(res.result, Exception)
