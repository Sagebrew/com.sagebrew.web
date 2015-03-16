from uuid import uuid1
from django.test import TestCase
from sb_solutions.utils import save_solution_util


class TestCreateSolutionUtil(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.solution_info_dict = {'content': 'test solution',
                                 'solution_uuid': str(uuid1()),}

    def test_save_solution_util(self):
        response = save_solution_util(**self.solution_info_dict)
        self.assertTrue(response)

    def test_save_existing_solution(self):
        save_solution_util(**self.solution_info_dict)
        response2 = save_solution_util(**self.solution_info_dict)
        self.assertTrue(response2)


