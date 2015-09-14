import time
from uuid import uuid1
import requests_mock
from django.contrib.auth.models import User
from django.test import RequestFactory

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_solutions.neo_models import Solution
from sb_comments.neo_models import Comment

from sb_questions.neo_models import Question
from sb_questions.views import question_detail_page


class TestGetQuestionSearchView(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.first_name = 'Tyler'
        self.pleb.last_name = 'Wiersing'
        self.pleb.save()

    def test_get_question_search_view_success(self):
        self.client.force_authenticate(user=self.user)
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)

        res = self.client.get('/conversations/search/%s/' %
                              question.object_uuid)
        self.assertTrue(res.status_code, status.HTTP_200_OK)


class TestGetQuestionView(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.first_name = 'Tyler'
        self.pleb.last_name = 'Wiersing'
        self.pleb.save()

    def test_get_question_view_success(self):
        self.client.force_authenticate(user=self.user)
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)

        res = self.client.get('/conversations/%s/' %
                              question.object_uuid)
        self.assertTrue(res.status_code, status.HTTP_200_OK)

    def test_get_question_view_html_snapshot_single_success(self):
        self.client.force_authenticate(user=self.user)
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)

        res = self.client.get('/conversations/%s/?_escaped_fragment_=' %
                              question.object_uuid)
        self.assertTrue(res.status_code, status.HTTP_200_OK)

    @requests_mock.mock()
    def test_get_question_view_html_snapshot_full_success(self, m):
        factory = RequestFactory()

        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        parent_url = reverse(
            '%s-detail' % question.get_child_label().lower(),
            kwargs={'object_uuid': question.object_uuid})
        question_object = {
            "id": "64770182-54d3-11e5-85db-080027ed9d41",
            "type": "question",
            "created": "2015-09-06T20:11:00.502411Z",
            "object_uuid": "64770182-54d3-11e5-85db-080027ed9d41",
            "content": "A new question for the newsfeedA new question for "
                       "the newsfeedA new question for the newsfeed",
            "upvotes": 1,
            "downvotes": 0,
            "vote_count": 1,
            "vote_type": None,
            "view_count": 1,
            "profile": "devon_bleibtrey",
            "url": "https://sagebrew.local.dev/conversations/"
                   "64770182-54d3-11e5-85db-080027ed9d41/",
            "last_edited_on": "2015-09-06T20:11:00.499200Z",
            "flagged_by": [],
            "council_vote": None,
            "is_closed": False,
            "html_content": "<p>A new question for the newsfeedA new question "
                            "for the newsfeedA new question for the"
                            " newsfeed</p>",
            "title": "A new question for the newsfeed",
            "href": "https://sagebrew.local.dev/v1/questions/64770182-54d3-"
                    "11e5-85db-080027ed9d41/",
            "tags": [
                "taxes"
            ],
            "solutions": [
                "a06881d4-54d3-11e5-85db-080027ed9d41"
            ],
            "solution_count": 1
        }
        m.get('%s' % parent_url, json=question_object,
              status_code=status.HTTP_200_OK)
        solution = Solution(content='this is fake content',
                            added_to_search_index=True,
                            owner_username=self.pleb.username).save()
        solution_object = {
            "id": "c2a21948-576e-11e5-85db-080027ed9d41",
            "type": "solution",
            "created": "2015-09-10T03:48:12.809150Z",
            "object_uuid": "c2a21948-576e-11e5-85db-080027ed9d41",
            "content": "from  from rest_framework.t_framtFactory",
            "upvotes": 1,
            "downvotes": 0,
            "vote_count": 1,
            "vote_type": True,
            "view_count": 0,
            "profile": "jack_bleibtrey",
            "url": "https://sagebrew.local.dev/conversations/"
                   "9c764c94-576e-11e5-85db-080027ed9d41/",
            "last_edited_on": "2015-09-10T03:48:12.808836Z",
            "flagged_by": [],
            "council_vote": None,
            "is_closed": False,
            "html_content": "<p>from rest_framework.test tory</p>",
            "href": "https://sagebrew.local.dev/v1/solutions/"
                    "c2a21948-576e-11e5-85db-080027ed9d41/",
            "solution_to": "https://sagebrew.local.dev/v1/"
                           "questions/9c764c94-576e-11e5-85db-080027ed9d41/"
        }
        parent_url = reverse(
            '%s-detail' % solution.get_child_label().lower(),
            kwargs={'object_uuid': solution.object_uuid})
        m.get('%s' % parent_url, json=solution_object,
              status_code=status.HTTP_200_OK)
        comment = Comment(content="test comment",
                          owner_username=self.pleb.username,
                          parent_type='question').save()
        question.owned_by.connect(self.pleb)
        solution.solution_to.connect(question)
        question.solutions.connect(solution)
        question.comments.connect(comment)
        comment.comment_on.connect(question)
        comment2 = Comment(content="test comment2",
                           owner_username=self.pleb.username,
                           parent_type='solution').save()
        solution.comments.connect(comment2)
        comment2.comment_on.connect(solution)
        request = factory.get('/conversations/%s/?_escaped_fragment_=' %
                              question.object_uuid)
        request.user = self.user
        response = question_detail_page(request,
                                        question_uuid=question.object_uuid)
        solution.comments.disconnect(comment2)
        question.comments.disconnect(comment)
        solution.delete()
        question.delete()
        comment.delete()
        comment2.delete()
        self.assertTrue(response.status_code, status.HTTP_200_OK)


class TestGetQuestionListView(APITestCase):
    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.pleb.first_name = 'Tyler'
        self.pleb.last_name = 'Wiersing'
        self.pleb.save()

    def test_get_question_view_success(self):
        self.client.force_authenticate(user=self.user)
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)

        res = self.client.get('/conversations/')
        self.assertTrue(res.status_code, status.HTTP_200_OK)

    def test_get_question_view_html_snapshot_single_success(self):
        self.client.force_authenticate(user=self.user)
        question = Question(object_uuid=str(uuid1()), content='test',
                            title=str(uuid1()),
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)

        res = self.client.get('/conversations/?_escaped_fragment_=')
        self.assertTrue(res.status_code, status.HTTP_200_OK)