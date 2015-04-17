import pytz
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.safestring import SafeText

from neomodel import CypherException

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_public_official.neo_models import BaseOfficial
from sb_public_official.utils import prepare_official_search_html



class TestPrepareSearchHTML(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_prepare_search_html(self):
        try:
            test_official = BaseOfficial(
                object_uuid = str(uuid1()),
                full_name="Test Rep",
                first_name="Test",
                last_name="Rep",
                start_date=datetime.now(pytz.utc),
                end_date=datetime.now(pytz.utc),
                state="MI",
                title="House Rep",
                district=11,
                current=True
            )
            test_official.save()
        except (CypherException, IOError):
            test_official = None

        res = prepare_official_search_html(test_official.object_uuid)
        self.assertIsInstance(res, SafeText)