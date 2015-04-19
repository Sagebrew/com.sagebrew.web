import time
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from sb_solutions.tasks import add_solution_to_search_index
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_solutions.neo_models import Solution


class TestAddSolutionToSearchIndexTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_add_solution_to_search_index_success(self):
        solution = Solution(content='this is fake content').save()
        solution.owned_by.connect(self.pleb)
        data = {"solution": solution}
        res = add_solution_to_search_index.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_add_solution_to_search_index_solution_already_added(self):
        solution = Solution(content='this is fake content',
                            added_to_search_index=True).save()
        solution.owned_by.connect(self.pleb)
        data = {"solution": solution}
        res = add_solution_to_search_index.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_add_solution_to_search_index_no_owner(self):
        solution = Solution(content='this is fake content').save()
        data = {"solution": solution}
        res = add_solution_to_search_index.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Exception)
