import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from sb_posts.neo_models import SBPost
from sb_questions.neo_models import SBQuestion
from sb_solutions.neo_models import SBSolution
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_base.tasks import create_object_relations_task


class TestCreateObjectRelationsTask(TestCase):
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

    def test_wall_pleb_is_not_none(self):
        post_info_dict = {'content': 'test post', 'object_uuid': str(uuid1())}
        post = SBPost(**post_info_dict)
        post.save()

        data={'sb_object': post,
              'current_pleb': self.pleb.email,
              'wall_pleb': self.pleb.email}
        response = create_object_relations_task.apply_async(kwargs=data)
        while not response.ready():
            time.sleep(3)
        self.assertTrue(response.result)

    def test_question_is_not_none(self):
        question_uuid = str(uuid1())
        solution_uuid = str(uuid1())
        SBQuestion(content="fake content", title="fake title",
                   object_uuid=question_uuid).save()
        solution = SBSolution(content="fake solution", object_uuid=solution_uuid).save()
        post_info_dict = {'content': 'test post', 'object_uuid': str(uuid1())}
        post = SBPost(**post_info_dict)
        post.save()

        data={'sb_object': solution,
              'current_pleb': self.pleb.email,
              'question': question_uuid}
        response = create_object_relations_task.apply_async(kwargs=data)
        while not response.ready():
            time.sleep(3)
        self.assertTrue(response.result)