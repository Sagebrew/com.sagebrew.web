from uuid import uuid1

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_privileges.neo_models import Privilege
from sb_requirements.neo_models import Requirement


class TestPrivilegeViews(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.privilege = Privilege(name=str(uuid1())).save()
        self.requirement = Requirement(name=str(uuid1()),
                                       url=settings.WEB_ADDRESS +
                                       "/v1/profiles/"
                                       "<username>/reputation/",
                                       key="reputation",
                                       operator="coperator\nge\np0\n.",
                                       condition=0).save()
        self.privilege.requirements.connect(self.requirement)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("privilege-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_privilege_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("privilege-detail",
                      kwargs={'name': self.privilege.name})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], self.privilege.name)
