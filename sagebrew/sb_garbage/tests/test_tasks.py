import time
from django.test.testcases import TestCase
from django.contrib.auth.models import User

from api.utils import test_wait_util
from sb_registration.utils import create_user_util
from plebs.neo_models import Pleb
from sb_garbage.tasks import empty_garbage_can
from sb_garbage.neo_models import SBGarbageCan

class TestGarbageCanTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_empty_garbage_can_exists(self):
        try:
            garbage = SBGarbageCan.nodes.get(garbage_can='garbage')
            garbage.delete()
        except SBGarbageCan.DoesNotExist:
            pass
        garbage = SBGarbageCan(garbage_can='garbage')
        garbage.save()
        res = empty_garbage_can.apply_async()
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)

    def test_empty_garbage_can_does_not_exist(self):
        try:
            garbage = SBGarbageCan.nodes.get(garbage_can='garbage')
        except SBGarbageCan.DoesNotExist:
            pass
        res = empty_garbage_can.apply_async()
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)