from django.contrib.auth.models import User
from django.test import TestCase

from api.utils import wait_util
from sb_registration.utils import create_user_util_test
from plebs.neo_models import Pleb
from sb_registration.utils import create_address_long_hash


class TestCreateAddressLongHash(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_create_address_long_hash_address2(self):
        address = {'primary_address': '125 glenwood dr',
                   'street_additional': 'apt 112',
                   'city': 'Walled Lake',
                   'state': 'MI',
                   'postal_code': 48390,
                   'country': "usa",
                   'latitude': 48.2189,
                   'longitude': 68.2131,
                   'congressional_district': 11}

        self.assertTrue(create_address_long_hash(address))

'''
class TestUploadImageUtil(TestCase):
    def test_upload_image_util(self):
        location = '%s/sb_posts/tests/images/' % settings.PROJECT_DIR
        res = upload_image('profile_pictures', 'test_image', location)
        # TODO grab res and delete image from S3
        self.assertIsInstance(res, str)
'''