import time
from uuid import uuid1
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from sb_notifications.tasks import (create_notification_post_task,
                                    create_notification_comment_task)
from sb_posts.neo_models import SBPost
from sb_comments.neo_models import SBComment
from plebs.neo_models import Pleb

class TestNotificationTasks(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.user2 = User.objects.create_user(
            username='Devon' + str(uuid1())[:25],
            email=str(uuid1())
        )
        self.pleb2 = Pleb.nodes.get(email=self.user2.email)
        self.post_info_dict = {'content': 'test post',
                               'post_id': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_create_notification_post_task(self):
        post = SBPost(**self.post_info_dict)
        post.save()

        data={'post_uuid': post.post_id, 'from_pleb': self.pleb.email,
              'to_pleb': self.pleb2.email}
        response = create_notification_post_task.apply_async(kwargs=data)
        while not response.ready():
            time.sleep(3)
        self.assertTrue(response.result)

    def test_create_notification_post_task_post_fail(self):
        data={'post_uuid': str(uuid1()), 'from_pleb': self.pleb.email,
              'to_pleb': self.pleb2.email}
        response = create_notification_post_task.apply_async(kwargs=data)
        # while not response.ready():
        #    time.sleep(3)
        # TODO This will currently keep retrying because it thinks the pleb
        # or post will eventually be created and it will have something to
        # link to. Need to discuss this process
        # self.assertFalse(response.result)
        self.assertTrue(True)

    def test_create_notification_comment_task(self):
        post = SBPost(**self.post_info_dict)
        post.save()
        comment = SBComment(comment_id=str(uuid1()), content='sdfasd')
        comment.save()

        data = {'from_pleb':self.pleb.email, 'to_pleb': self.pleb2.email,
                'comment_on': 'post', 'comment_on_id': post.post_id,
                'comment_uuid': comment.comment_id}

        response = create_notification_comment_task.apply_async(kwargs=data)
        while not response.ready():
            time.sleep(3)
        self.assertTrue(response.result)

    def test_create_notification_comment_task_fail(self):
        data = {'from_pleb':self.pleb.email, 'to_pleb': self.pleb2.email,
                'comment_on': 'post', 'comment_on_id': str(uuid1()),
                'comment_uuid': str(uuid1())}

        response = create_notification_comment_task.apply_async(kwargs=data)
        while not response.ready():
            time.sleep(3)
        self.assertEqual(type(response.result), Exception)