from uuid import uuid1

from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from django.test import TestCase


from plebs.neo_models import Pleb
from api.utils import wait_util
from sb_registration.utils import create_user_util_test
from sb_votes.views import vote_object_view


class TestVoteObjectView(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_vote_object_view_success(self):
        data = {
            'object_type': '0274a216-644f-11e4-9ad9-080027242395',
            'object_uuid': str(uuid1()),
            'current_pleb': self.email,
            'vote_type': False,
            'upvote_count': 0,
            'downvote_count': 0
        }
        request = self.factory.post('/vote/vote_object_api/', data=data,
                                    format='json')
        request.user = self.user
        res = vote_object_view(request)

        self.assertEqual(res.status_code, 200)

    def test_vote_object_view_invalid_form(self):
        data = {
            'objecasdft_type': '0274a216-644f-11e4-9ad9-080027242395',
            'object_uuid': str(uuid1()),
            'current_pleb': self.email,
            'vote_type': False
        }
        request = self.factory.post('/vote/vote_object_api/', data=data,
                                    format='json')
        request.user = self.user
        res = vote_object_view(request)

        self.assertEqual(res.status_code, 400)

    def test_vote_object_view_invalid_data_type(self):
        data = 123151
        request = self.factory.post('/vote/vote_object_api/', data=data,
                                    format='json')
        request.user = self.user
        res = vote_object_view(request)

        self.assertEqual(res.status_code, 400)
