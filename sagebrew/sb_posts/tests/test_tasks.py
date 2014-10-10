import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command

from sb_posts.neo_models import SBPost
from sb_posts.tasks import (delete_post_and_comments, save_post_task,
                            edit_post_info_task,
                            create_downvote_post, create_upvote_post,
                            flag_post_task)
from plebs.neo_models import Pleb


class TestSavePostTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_save_post_task(self):
        response = save_post_task.apply_async(kwargs=self.post_info_dict)
        while not response.ready():
            time.sleep(1)
        response = response.result
        self.assertTrue(response)

class TestDeletePostTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_delete_post_task(self):
        post = SBPost(content=self.post_info_dict['content'],
                      post_id=self.post_info_dict['post_uuid'])
        post.save()
        delete_response = delete_post_and_comments.apply_async(
            [self.post_info_dict['post_uuid'], ])
        while not delete_response.ready():
            time.sleep(1)
        delete_response = delete_response.result
        self.assertTrue(delete_response)

class TestEditPostTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_edit_post_task(self):
        post = SBPost(post_id=uuid1(), content="test post")
        post.last_edited_on = datetime.now(pytz.utc)
        post.save()
        edit_post_dict = {'content': 'Post edited',
                          'post_uuid': post.post_id,
                          'current_pleb': self.pleb.email}
        edit_response = edit_post_info_task.apply_async(kwargs=edit_post_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result
        self.assertTrue(edit_response)



class TestPostTaskRaceConditions(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_race_condition_edit_delete_post_tasks(self):
        edit_post_dict = {'content': 'Post edited',
                          'post_uuid': self.post_info_dict['post_uuid'],
                          'current_pleb': self.pleb.email,
                          'last_edited_on': datetime.now(pytz.utc)}
        save_response = save_post_task.apply_async(kwargs=self.post_info_dict)
        while not save_response.ready():
            time.sleep(1)
        save_response = save_response.result
        edit_response = edit_post_info_task.apply_async(kwargs=edit_post_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result
        delete_response = delete_post_and_comments.apply_async(
            [self.post_info_dict['post_uuid'], ])
        while not delete_response.ready():
            time.sleep(1)
        delete_response = delete_response.result
        self.assertTrue(save_response)
        self.assertTrue(edit_response)
        self.assertTrue(delete_response)

    def test_race_condition_edit_multiple_times(self):
        edit_array = []
        post = SBPost(content="test post")
        post.save()

        edit_dict = {'content': "post edited",
                     'post_uuid': post.post_id,
                     'current_pleb': self.pleb.email,
                     'last_edited_on': datetime.now(pytz.utc)}
        for num in range(1, 10):
            edit_dict['content'] = "post edited" + str(uuid1())
            edit_dict['last_edited_on'] = datetime.now(pytz.utc)
            edit_response = edit_post_info_task.apply_async(kwargs=edit_dict)
            while not edit_response.ready():
                time.sleep(1)
            edit_response = edit_response.result
            edit_array.append(edit_response)

        for response in edit_array:
            self.assertTrue(response)


class TestMultipleTasks(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_create_many_posts(self):
        response_array = []
        for num in range(1, 10):
            uuid = str(uuid1())
            self.post_info_dict['post_uuid'] = uuid
            save_response = save_post_task.apply_async(
                kwargs=self.post_info_dict)
            while not save_response.ready():
                time.sleep(1)
            save_response = save_response.result
            response_array.append(save_response)

        for item in response_array:
            self.assertTrue(item)

    def test_create_many_votes(self):
        vote_array = []
        vote_info_dict = {"post_uuid": self.post_info_dict['post_uuid'],
                          "pleb": self.pleb.email}
        response = save_post_task.apply_async(kwargs=self.post_info_dict)
        while not response.ready():
            time.sleep(1)
        response = response.result

        for num in range(1, 10):
            uvote_response = create_upvote_post.apply_async(
                kwargs=vote_info_dict)
            dvote_response = create_downvote_post.apply_async(
                kwargs=vote_info_dict)
            while not uvote_response.ready():
                time.sleep(1)
            uvote_response = uvote_response.result
            while not dvote_response.ready():
                time.sleep(1)
            dvote_response = dvote_response.result
            vote_array.append(uvote_response)
            vote_array.append(dvote_response)

        self.assertTrue(response)
        for item in vote_array:
            self.assertTrue(item)

class TestFlagPostTask(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Tyler', email=str(uuid1())+'@gmail.com')
        self.pleb = Pleb.nodes.get(email=self.user.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

    def tearDown(self):
        call_command('clear_neo_db')

    def test_flag_post_task_success_spam(self):
        post = SBPost(post_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.post_id, 'current_user': self.pleb.email,
                     'flag_reason': 'spam'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

    def test_flag_post_task_success_explicit(self):
        post = SBPost(post_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.post_id, 'current_user': self.pleb.email,
                     'flag_reason': 'explicit'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)

    def test_flag_post_task_success_other(self):
        post = SBPost(post_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.post_id, 'current_user': self.pleb.email,
                     'flag_reason': 'other'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)

    def test_flag_post_task_failure_incorrect_reason(self):
        post = SBPost(post_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.post_id, 'current_user': self.pleb.email,
                     'flag_reason': 'dumb'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertEqual(type(res), Exception)

    def test_flag_post_task_post_does_not_exist(self):
        task_dict = {'post_uuid': uuid1(), 'current_user': self.pleb.email,
                     'flag_reason': 'other'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertEqual(type(res), Exception)

    def test_flag_post_task_user_does_not_exist(self):
        post = SBPost(post_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.post_id, 'current_user': uuid1(),
                     'flag_reason': 'other'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertEqual(type(res), Exception)