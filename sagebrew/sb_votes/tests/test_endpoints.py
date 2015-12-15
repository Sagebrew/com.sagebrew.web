from uuid import uuid1

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase

from api.utils import spawn_task
from plebs.neo_models import Pleb
from sb_docstore.tasks import spawn_user_updates
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question


class VoteEndpointTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.unit_under_test_name = 'goal'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        self.question = Question(title=str(uuid1())).save()

    def test_vote_get(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("question-detail",
                      kwargs={'object_uuid': self.question.object_uuid})
        res = self.client.get(url + "votes/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_vote_create(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "vote_type": True
        }
        url = reverse("question-detail",
                      kwargs={'object_uuid': self.question.object_uuid})
        res = self.client.post(url + "votes/", data=data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_vote_create_pleb_is_not_verified(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "vote_type": True
        }
        url = reverse("question-detail",
                      kwargs={'object_uuid': self.question.object_uuid})
        self.pleb.is_verified = False
        self.pleb.save()
        cache.clear()
        res = self.client.post(url + "votes/", data=data, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.pleb.is_verified = True
        self.pleb.save()

    def test_vote_no_task_in_cache(self):
        self.client.force_authenticate(user=self.user)
        cache.delete("%s_%s_vote" % (self.user.username,
                                     self.question.object_uuid))
        data = {
            "vote_type": True
        }
        url = reverse("question-detail",
                      kwargs={'object_uuid': self.question.object_uuid})
        res = self.client.post(url + "votes/", data=data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_vote_task_in_cache(self):
        self.client.force_authenticate(user=self.user)
        task_params = {
            "username": self.user.username,
            "object_uuid": self.question.object_uuid
        }
        async_result = spawn_task(task_func=spawn_user_updates,
                                  task_param=task_params, countdown=30)
        cache.set("%s_%s_vote" % (self.user.username,
                                  self.question.object_uuid), async_result)
        data = {
            "vote_type": True
        }
        url = reverse("question-detail",
                      kwargs={'object_uuid': self.question.object_uuid})
        res = self.client.post(url + "votes/", data=data, format="json")
        # PENDING denotes a tack which either is waiting for execution or
        # unknown, if a task does not exist(has been revoked) state == PENDING
        # http://docs.celeryproject.org/en/latest/userguide/tasks.html#pending
        self.assertEqual(async_result.state, "PENDING")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
