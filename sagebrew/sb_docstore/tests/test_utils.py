import pytz
from json import dumps
from uuid import uuid1
from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils import wait_util
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util
from sb_questions.neo_models import SBQuestion
from sb_posts.neo_models import SBPost
from sb_comments.neo_models import SBComment
from sb_docstore.utils import (connect_to_dynamo, add_object_to_table,
                               query_parent_object_table, update_doc,
                               get_question_doc, build_question_page,
                               get_vote, update_vote, get_vote_count,
                               get_wall_docs, build_wall_docs,
                               get_user_updates)

class TestSaveComments(TestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util("test", "test", self.email, "testpassword")
        self.assertNotEqual(res, False)
        wait_util(res)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)

    def test_add_object_to_table_success(self):
        data = {"email": self.pleb.email, "username": self.pleb.username,
                "first_name": self.pleb.first_name,
                "last_name": self.pleb.last_name}
        res = add_object_to_table("users_full", data)

        self.assertTrue(res)

    def test_add_object_to_table_failure(self):
        data = {"username": self.pleb.username,
                "first_name": self.pleb.first_name}
        res = add_object_to_table("users_full", data)

        self.assertIsInstance(res, Exception)

    def test_query_parent_object_table_success(self):
        uuid = str(uuid1())
        res = query_parent_object_table(uuid, True)

        self.assertIsInstance(res, list)

    def test_query_parent_object_table_get_one(self):
        uuid = str(uuid1())
        timestamp = unicode(datetime.now(pytz.utc))
        data = {'parent_object': uuid, "datetime": timestamp, "content": '123',
                'user': self.pleb.email}
        res = add_object_to_table('edits', object_data=data)
        self.assertTrue(res)

        res = query_parent_object_table(uuid)

        self.assertEqual(res, data)

    def test_update_doc(self):
        uuid = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        data = {"parent_object": uuid, "time": now, "user": self.pleb.email,
                "status": 1, "object_uuid": uuid}
        update_data = [{'update_key': 'status', 'update_value': 2}]
        res = add_object_to_table('public_questions', data)
        self.assertTrue(res)

        res = update_doc('public_questions', uuid, update_data)

        self.assertFalse(isinstance(res, Exception))

    def test_update_doc_parent_object(self):
        uuid = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        data = {"parent_object": uuid, "time": now, "user": self.pleb.email,
                "status": 1, "object_uuid": uuid}
        update_data = [{'update_key': 'status', 'update_value': 2}]
        res = add_object_to_table('public_solutions', data)
        self.assertTrue(res)

        res = update_doc('public_solutions', uuid, update_data, uuid)

        self.assertFalse(isinstance(res, Exception))

    def test_update_doc_datetime(self):
        uuid = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        data = {"parent_object": uuid, "datetime": now, "user": self.pleb.email,
                "status": 1, "object_uuid": uuid}
        update_data = [{'update_key': 'status', 'update_value': 2}]
        res = add_object_to_table('posts', data)
        self.assertTrue(res)

        res = update_doc('posts', uuid, update_data, uuid, now)

        self.assertFalse(isinstance(res, Exception))

    def test_get_question_doc(self):
        uuid = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        data = {'object_uuid': uuid, 'content': '1231231231',
                'user': self.pleb.email, 'datetime': now}
        res = add_object_to_table('public_questions', data)
        self.assertTrue(res)
        solution_uuid = str(uuid1())
        solution_data = {'parent_object': uuid, 'object_uuid': solution_uuid,
                         'content': '12312312', 'datetime': now}
        sol_res = add_object_to_table('public_solutions', solution_data)
        self.assertTrue(sol_res)
        res = get_question_doc(uuid, 'public_questions', 'public_solutions')
        self.assertIsInstance(res, dict)

    def test_build_question_page(self):
        question = SBQuestion(sb_id=str(uuid1()), content="1231",
                              question_title="12312312").save()
        question.owned_by.connect(self.pleb)
        res = build_question_page(question.sb_id, 'public_questions',
                                  'public_solutions')
        self.assertTrue(res)

    def test_get_vote(self):
        uuid = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        vote_data = {
            'parent_object': uuid,
            'user': self.pleb.email,
            'status': 1,
            'datetime': now
        }
        res = add_object_to_table('votes', vote_data)
        self.assertTrue(res)

        res = get_vote(uuid, self.pleb.email)

        self.assertNotEqual(res, False)
        self.assertFalse(isinstance(res, Exception))

    def test_update_vote(self):
        uuid = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        vote_data = {
            'parent_object': uuid,
            'user': self.pleb.email,
            'status': 1,
            'datetime': now
        }
        res = add_object_to_table('votes', vote_data)
        self.assertTrue(res)

        res = update_vote(uuid, self.pleb.email, 0, now)
        self.assertNotEqual(res, False)
        self.assertFalse(isinstance(res, Exception))

    def test_get_vote_count(self):
        uuid = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        vote_data = {
            'parent_object': uuid,
            'user': self.pleb.email,
            'status': 1,
            'datetime': now
        }
        res = add_object_to_table('votes', vote_data)
        self.assertTrue(res)

        res = get_vote_count(uuid, 1)

        self.assertEqual(res, 1)

    def test_get_wall_doc(self):
        post_id = str(uuid1())
        comment_id = str(uuid1())
        now = unicode(datetime.now(pytz.utc))
        post_data = {
            'parent_object': self.pleb.email, 'datetime': now,
            'object_uuid': post_id, 'content': 'a3lk4jq;w2jr'
        }
        comment_data = {
            'parent_object': post_id, 'object_uuid': comment_id,
            'datetime': now, 'content': 'a;sldkf;lajsdkfjas;df'
        }
        post_res = add_object_to_table('posts', post_data)
        self.assertTrue(post_res)
        comment_res = add_object_to_table('comments', comment_data)
        self.assertTrue(comment_res)

        res = get_wall_docs(self.pleb.email)

        self.assertNotEqual(res, False)
        self.assertFalse(isinstance(res, Exception))

    def test_build_wall_docs(self):
        post = SBPost(sb_id=str(uuid1()), content='a;sdlkfj;asd').save()
        post.owned_by.connect(self.pleb)
        post.posted_on_wall.connect(self.pleb.wall.all()[0])
        comment = SBComment(sb_id=str(uuid1()),
                            content='A:KFj;LKAJFD:Sk').save()
        post.comments.connect(comment)
        comment.owned_by.connect(self.pleb)

        res = build_wall_docs(self.pleb)

        self.assertTrue(res)

    def test_get_user_updates(self):
        pass