import pytz
import time
from uuid import uuid1
from datetime import datetime
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from celery.utils.serialization import UnpickleableExceptionWrapper
from neomodel.exception import DoesNotExist

from api.utils import test_wait_util
from sb_posts.neo_models import SBPost
from sb_posts.tasks import (delete_post_and_comments, save_post_task,
                            edit_post_info_task,
                            create_downvote_post, create_upvote_post,
                            flag_post_task)
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util

class TestSavePostTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_save_post_task(self):
        response = save_post_task.apply_async(kwargs=self.post_info_dict)
        while not response.ready():
            time.sleep(1)
        response = response.result
        self.assertTrue(response)

class TestDeletePostTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_delete_post_task(self):
        post = SBPost(content=self.post_info_dict['content'],
                      sb_id=self.post_info_dict['post_uuid'])
        post.save()
        delete_response = delete_post_and_comments.apply_async(
            [self.post_info_dict['post_uuid'], ])
        while not delete_response.ready():
            time.sleep(1)
        delete_response = delete_response.result
        self.assertTrue(delete_response)

class TestEditPostTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_edit_post_task_success(self):
        post = SBPost(sb_id=uuid1(), content="test post")
        post.last_edited_on = datetime.now(pytz.utc)
        post.save()
        edit_post_dict = {'content': 'Post edited',
                          'post_uuid': post.sb_id,
                          'current_pleb': self.pleb.email}
        edit_response = edit_post_info_task.apply_async(kwargs=edit_post_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result
        self.assertTrue(edit_response)

    def test_edit_post_task_failure_post_does_not_exist(self):
        edit_post_dict = {'content': 'Post edited',
                          'post_uuid': str(uuid1()),
                          'current_pleb': self.pleb.email}
        edit_response = edit_post_info_task.apply_async(kwargs=edit_post_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result
        print edit_response
        self.assertTrue(isinstance(edit_response, DoesNotExist))

    def test_edit_post_task_failure_content_is_the_same(self):
        post = SBPost(sb_id=uuid1(), content="test post")
        post.last_edited_on = datetime.now(pytz.utc)
        post.save()
        edit_post_dict = {'content': 'test post',
                          'post_uuid': post.sb_id,
                          'current_pleb': self.pleb.email}
        edit_response = edit_post_info_task.apply_async(kwargs=edit_post_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result
        self.assertFalse(edit_response)

    def test_edit_post_task_failure_to_be_deleted(self):
        post = SBPost(sb_id=uuid1(), content="test post")
        post.last_edited_on = datetime.now(pytz.utc)
        post.to_be_deleted = True
        post.save()
        edit_post_dict = {'content': 'test edit',
                          'post_uuid': post.sb_id,
                          'current_pleb': self.pleb.email}
        edit_response = edit_post_info_task.apply_async(kwargs=edit_post_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result
        self.assertFalse(edit_response)

    def test_edit_post_task_failure_same_timestamp(self):
        now = datetime.now(pytz.utc)
        post = SBPost(sb_id=uuid1(), content="test post")
        post.last_edited_on = now
        post.to_be_deleted = True
        post.save()
        edit_post_dict = {'content': 'test edit',
                          'post_uuid': post.sb_id,
                          'current_pleb': self.pleb.email,
                          'last_edited_on': now}
        edit_response = edit_post_info_task.apply_async(kwargs=edit_post_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result
        self.assertFalse(edit_response)

    def test_edit_post_task_failure_last_edit_more_recent(self):
        now = datetime.now(pytz.utc)
        post = SBPost(sb_id=uuid1(), content="test post")
        post.last_edited_on = datetime.now(pytz.utc)
        post.to_be_deleted = True
        post.save()
        edit_post_dict = {'content': 'test edit',
                          'post_uuid': post.sb_id,
                          'current_pleb': self.pleb.email,
                          'last_edited_on': now}
        edit_response = edit_post_info_task.apply_async(kwargs=edit_post_dict)
        while not edit_response.ready():
            time.sleep(1)
        edit_response = edit_response.result
        self.assertFalse(edit_response)


class TestPostVoteTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_upvote_post_success(self):
        post = SBPost(sb_id=str(uuid1()))
        post.save()
        task_data = {
            "pleb": self.pleb.email,
            "post_uuid": post.sb_id
        }
        res = create_upvote_post.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

    def test_upvote_post_failure_post_does_not_exist(self):
        post = SBPost(sb_id=str(uuid1()))
        post.save()
        task_data = {
            "pleb": self.pleb.email,
            "post_uuid": str(uuid1())
        }
        res = create_upvote_post.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(isinstance(res, DoesNotExist))

    def test_upvote_post_failure_pleb_does_not_exist(self):
        post = SBPost(sb_id=str(uuid1()))
        post.save()
        task_data = {
            "pleb": str(uuid1()),
            "post_uuid": post.sb_id
        }
        res = create_upvote_post.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)

    def test_downvote_post_success(self):
        post = SBPost(sb_id=str(uuid1()))
        post.save()
        task_data = {
            "pleb": self.pleb.email,
            "post_uuid": post.sb_id
        }
        res = create_downvote_post.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

    def test_downvote_post_failure_post_does_not_exist(self):
        post = SBPost(sb_id=str(uuid1()))
        post.save()
        task_data = {
            "pleb": self.pleb.email,
            "post_uuid": str(uuid1())
        }
        res = create_downvote_post.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(isinstance(res, DoesNotExist))

    def test_downvote_post_failure_pleb_does_not_exist(self):
        post = SBPost(sb_id=str(uuid1()))
        post.save()
        task_data = {
            "pleb": str(uuid1()),
            "post_uuid": post.sb_id
        }
        res = create_downvote_post.apply_async(kwargs=task_data)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertFalse(res)



class TestPostTaskRaceConditions(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}

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
                     'post_uuid': post.sb_id,
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
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}


    def test_create_many_posts(self):
        response_array = []
        for num in range(1, 10):
            uuid = str(uuid1())
            self.post_info_dict['post_uuid'] = uuid
            save_response = save_post_task.apply_async(
                kwargs=self.post_info_dict)
            while not save_response.ready():
                time.sleep(1)
            response_array.append(save_response.result)

        self.assertNotIn(False, response_array)

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
            while not dvote_response.ready():
                time.sleep(1)
            vote_array.append(uvote_response.result)
            vote_array.append(dvote_response.result)

        self.assertTrue(response)
        self.assertNotIn(False, vote_array)

class TestFlagPostTask(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        test_wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.post_info_dict = {'current_pleb': self.pleb.email,
                               'wall_pleb': self.pleb.email,
                               'content': 'test post',
                               'post_uuid': str(uuid1())}
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_flag_post_task_success_spam(self):
        post = SBPost(sb_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.sb_id, 'current_user': self.pleb.email,
                     'flag_reason': 'spam'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result

        self.assertTrue(res)

    def test_flag_post_task_success_explicit(self):
        post = SBPost(sb_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.sb_id, 'current_user': self.pleb.email,
                     'flag_reason': 'explicit'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)

    def test_flag_post_task_success_other(self):
        post = SBPost(sb_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.sb_id, 'current_user': self.pleb.email,
                     'flag_reason': 'other'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        self.assertTrue(res)

    def test_flag_post_task_failure_incorrect_reason(self):
        post = SBPost(sb_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.sb_id, 'current_user': self.pleb.email,
                     'flag_reason': 'dumb'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        print res
        self.assertTrue(isinstance(res, Exception))

    def test_flag_post_task_post_does_not_exist(self):
        task_dict = {'post_uuid': uuid1(), 'current_user': self.pleb.email,
                     'flag_reason': 'other'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        print res
        self.assertTrue(isinstance(res, Exception))

    def test_flag_post_task_user_does_not_exist(self):
        post = SBPost(sb_id=uuid1())
        post.save()
        task_dict = {'post_uuid': post.sb_id, 'current_user': uuid1(),
                     'flag_reason': 'other'}

        res = flag_post_task.apply_async(kwargs=task_dict)
        while not res.ready():
            time.sleep(1)
        res = res.result
        print res
        self.assertTrue(isinstance(res, Exception))