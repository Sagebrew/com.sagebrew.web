from requests import get
from django.test.testcases import TestCase

from govtrack.utils import create_gt_role, create_gt_person

class TestCreateGTRoleUtil(TestCase):
    def setUp(self):
        self.role_url = 'https://www.govtrack.us/api/v2/role?limit=1'
        self.role_dict = get(self.role_url).json()

    def test_create_gt_role_success(self):
        res = create_gt_role(self.role_dict['objects'][0])
        self.assertIsNot(res, False)

class TestCreateGTPerson(TestCase):
    def setUp(self):
        self.role_url = 'https://www.govtrack.us/api/v2/role?limit=1'
        self.role_dict = get(self.role_url).json()

    def test_create_gt_person_success(self):
        res = create_gt_person(self.role_dict['objects'][0]['person'])
        self.assertIsNot(res, False)