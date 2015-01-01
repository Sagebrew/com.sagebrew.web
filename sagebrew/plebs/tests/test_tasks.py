import time
from uuid import uuid1
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util
from plebs.tasks import (create_pleb_task, create_wall_task,
                         finalize_citizen_creation, send_email_task)
from sb_wall.neo_models import SBWall


class TestCreatePlebTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.username = res["username"]
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        try:
            pleb = Pleb.nodes.get(email='suppressionlist@simulator.amazonses.com')
            pleb.delete()
            user = User.objects.get(email='suppressionlist@simulator.amazonses.com')
            user.delete()
        except (Pleb.DoesNotExist, User.DoesNotExist):
            self.fake_user = User.objects.create_user(
                first_name='test', last_name='test',
                email='suppressionlist@simulator.amazonses.com', password='fakepass',
                username='thisisafakeusername')
            self.fake_user.save()

    def tearDown(self):
        self.fake_user.delete()
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_pleb_task_success_pleb_does_not_exist(self):
        task_data = {'user_instance': self.fake_user}

        res = create_pleb_task.apply_async(kwargs=task_data)

        while not res.ready():
            time.sleep(1)

        self.assertFalse(isinstance(res.result, Exception))

    def test_create_pleb_task_success_pleb_exists(self):
        user_instance = User.objects.get(username=self.username)
        task_data = {'user_instance': user_instance}

        res = create_pleb_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        self.assertFalse(isinstance(res.result, Exception))


class TestCreateWallTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        try:
            pleb = Pleb.nodes.get(
                email='suppressionlist@simulator.amazonses.com',
                username="thisthat")
            pleb.delete()
            user = User.objects.get(
                email='suppressionlist@simulator.amazonses.com',
                username="thisthat")
            user.delete()
        except (Pleb.DoesNotExist, User.DoesNotExist):
            pass
        self.fake_user = User.objects.create_user(
            first_name='test', last_name='test',
            email='suppressionlist@simulator.amazonses.com',
            password='fakepass',
            username='thisisafakeusername')
        self.fake_user.save()
        self.fake_pleb = Pleb(email=self.fake_user.email,
                              username=self.fake_user.username).save()

    def tearDown(self):
        self.fake_pleb.delete()
        self.fake_user.delete()
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_wall_task_success(self):
        task_data = {
            'user_instance': self.fake_user
        }
        res = create_wall_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(isinstance(res.result, Exception))

    def test_create_wall_task_pleb_has_wall(self):
        wall = SBWall(wall_id=str(uuid1())).save()
        wall.owner.connect(self.fake_pleb)
        self.fake_pleb.wall.connect(wall)
        task_data = {
            'user_instance': self.fake_user,
        }

        res = create_wall_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(isinstance(res.result, Exception))

    def test_create_wall_task_pleb_has_more_than_one_wall(self):
        wall = SBWall(wall_id=str(uuid1())).save()
        wall2 = SBWall(wall_id=str(uuid1())).save()
        wall.owner.connect(self.fake_pleb)
        self.fake_pleb.wall.connect(wall)
        self.fake_pleb.wall.connect(wall2)
        task_data = {
            'user_instance': self.fake_user,
        }

        res = create_wall_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(res.result)


class TestFinalizeCitizenCreationTask(TestCase):
    def setUp(self):
        self.email2 = 'suppressionlist@simulator.amazonses.com'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        try:
            pleb = Pleb.nodes.get(email=self.email2)
            pleb.delete()
            user = User.objects.get(email=self.email2)
            user.delete()
        except (Pleb.DoesNotExist, User.DoesNotExist):
            pass
        self.fake_user = User.objects.create_user(
            first_name='fake', last_name='user',
            email='suppressionlist@simulator.amazonses.com', password='fakepass',
            username='thisisafakeusername1')
        self.fake_user.save()
        self.fake_pleb = Pleb(email=self.fake_user.email,
                              first_name=self.fake_user.first_name,
                              last_name=self.fake_user.last_name,
                              username=self.fake_user.username).save()

    def tearDown(self):
        self.fake_pleb.delete()
        self.fake_user.delete()
        settings.CELERY_ALWAYS_EAGER = False

    def test_finalize_citizen_creation_email_not_sent(self):
        task_data = {
            'user_instance': self.fake_user
        }
        res = finalize_citizen_creation.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertNotIsInstance(res.result, Exception)

    def test_finalize_citizen_creation_email_sent(self):
        self.fake_pleb.initial_verification_email_sent = True
        self.fake_pleb.save()
        task_data = {
            'user_instance': self.fake_user
        }
        res = finalize_citizen_creation.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertNotIsInstance(res.result, Exception)


class TestSendEmailTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True
        try:
            pleb = Pleb.nodes.get(email='suppressionlist@simulator.amazonses.com')
            pleb.delete()
            user = User.objects.get(email='suppressionlist@simulator.amazonses.com')
            user.delete()
        except (Pleb.DoesNotExist, User.DoesNotExist):
            pass
        self.fake_user = User.objects.create_user(
            first_name='test', last_name='test',
            email='suppressionlist@simulator.amazonses.com', password='fakepass',
            username='thisisafakeusername')
        self.fake_user.save()
        self.fake_pleb = Pleb(email=self.fake_user.email,
                              first_name=self.fake_user.first_name,
                              last_name=self.fake_user.last_name).save()

    def tearDown(self):
        self.fake_pleb.delete()
        self.fake_user.delete()
        settings.CELERY_ALWAYS_EAGER = False

    def test_send_email_task(self):
        task_data = {'to': self.fake_pleb.email,
                     'subject': 'This is a fake subject',
                     'html_content': "<div>Fake HTML Content</div>"}
        res = send_email_task.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)

        self.assertFalse(isinstance(res.result, Exception))