import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from sb_solutions.tasks import save_solution_task, add_solution_to_search_index
from sb_questions.neo_models import SBQuestion
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_solutions.neo_models import SBSolution


class TestSaveSolutionTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.question_info_dict = {'question_title': "Test question",
                                   'content': 'test post',}
        self.solution_info_dict = {'current_pleb': self.email,
                                 'content': 'test solution'}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False


    def test_save_solution_task(self):
        self.question_info_dict['object_uuid']=str(uuid1())
        question = SBQuestion(**self.question_info_dict).save()
        question.owned_by.connect(self.pleb)
        self.solution_info_dict['question_uuid'] = question.object_uuid
        save_response = save_solution_task.apply_async(
            kwargs=self.solution_info_dict)

        while not save_response.ready():
            time.sleep(1)
        save_response = save_response.result

        self.assertTrue(save_response)

    def test_save_solution_task_fail_question_does_not_exist(self):
        question_uuid = str(uuid1())
        self.solution_info_dict["question_uuid"] = question_uuid
        save_response = save_solution_task.apply_async(
            kwargs=self.solution_info_dict)

        while not save_response.ready():
            time.sleep(1)
        save_response = save_response.result

        self.assertIsInstance(save_response, Exception)

    def test_save_solution_task_pleb_does_not_exist(self):
        self.question_info_dict['object_uuid']=str(uuid1())
        question = SBQuestion(**self.question_info_dict).save()
        question.owned_by.connect(self.pleb)
        self.solution_info_dict['question_uuid'] = question.object_uuid
        self.solution_info_dict['current_pleb'] = str(uuid1())
        self.solution_info_dict['solution_uuid'] = str(uuid1())
        save_response = save_solution_task.apply_async(
            kwargs=self.solution_info_dict)

        while not save_response.ready():
            time.sleep(1)
        save_response = save_response.result

        self.assertIsInstance(save_response, SBSolution)


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
        solution = SBSolution(object_uuid=str(uuid1()),
                          content='this is fake content').save()
        solution.owned_by.connect(self.pleb)
        data = {"solution": solution}
        res = add_solution_to_search_index.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_add_solution_to_search_index_solution_already_added(self):
        solution = SBSolution(object_uuid=str(uuid1()),
                          content='this is fake content',
                          added_to_search_index=True).save()
        solution.owned_by.connect(self.pleb)
        data = {"solution": solution}
        res = add_solution_to_search_index.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertTrue(res.result)

    def test_add_solution_to_search_index_no_owner(self):
        solution = SBSolution(object_uuid=str(uuid1()),
                          content='this is fake content').save()
        data = {"solution": solution}
        res = add_solution_to_search_index.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)

        self.assertIsInstance(res.result, Exception)