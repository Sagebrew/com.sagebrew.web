from uuid import uuid1
import time
from dateutil import parser

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase

from neomodel.exception import DoesNotExist

from plebs.neo_models import Pleb
from sb_tags.neo_models import Tag
from sb_questions.neo_models import Question
from sb_solutions.neo_models import Solution
from sb_registration.utils import create_user_util_test


class QuestionEndpointTests(APITestCase):
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.title = str(uuid1())
        self.question = Question(content="Hey I'm a question",
                                 title=self.title,
                                 owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(self.question)
        self.user = User.objects.get(email=self.email)
        try:
            Tag.nodes.get(name='taxes')
        except DoesNotExist:
            Tag(name='taxes').save()
        try:
            Tag.nodes.get(name='fiscal')
        except DoesNotExist:
            Tag(name='fiscal').save()
        try:
            Tag.nodes.get(name='environment')
        except DoesNotExist:
            Tag(name='environment').save()

    def test_unauthorized(self):
        url = reverse('question-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_missing_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = "This is a question that must be asked. What is blue?"
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_duplicate_title(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        response_duplicate = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_duplicate.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_duplicate.data['title'][0],
                         'Sorry looks like a Question with that '
                         'Title already exists.')

    def test_create_rendered(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        tags = ['taxes', 'environment']
        url = "%s?html=true" % reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("html" in response.data)
        self.assertTrue("ids" in response.data)
        self.assertEqual(len(response.data['ids']), 1)
        self.assertEqual(len(response.data['html']), 1)

    def test_create_content(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['content'], content)

    def test_create_title(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['title'], title)

    def test_create_tags(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.data['tags'][0], tags)
        self.assertIn(response.data['tags'][1], tags)
        self.assertEqual(len(response.data['tags']), 2)

    def test_create_profile(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['profile'], self.user.username)

    def test_create_type(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['type'], 'question')

    def test_create_no_title(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "title": "",
            "content": content,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['title'],
                         ['This field may not be blank.'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_content(self):
        self.client.force_authenticate(user=self.user)
        title = str(uuid1())
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "title": title,
            "content": "",
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['content'],
                         ['This field may not be blank.'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_tags(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_content_too_short(self):
        self.client.force_authenticate(user=self.user)
        content = "Short content."
        title = str(uuid1())
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['content'],
                         ['Ensure this field has at least 15 characters.'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_title_too_short(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = "Short?"
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['title'],
                         ['Ensure this field has at least 15 characters.'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_title_too_long(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = "Super long question that goes on and on and on for the " \
                "entire world to see. No one will read this entire question " \
                "and there's no way it only encompasses one thing. People " \
                "should really be less long winded. We wouldn't be able to " \
                "display this title nicely in any of our templates... Why " \
                "don't people think about the children?"
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['title'],
                         ['Ensure this field has no more than 140 characters.'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_too_many_tags(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        Tag(name='pension').save()
        Tag(name='income').save()
        Tag(name='foreign_policy').save()
        tags = ['taxes', 'environment', 'fiscal', 'pension', 'income',
                'foreign_policy']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['tags'], ['Only allow up to 5 tags'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        tag = Tag.nodes.get(name='fiscal')
        tag.delete()
        tag = Tag.nodes.get(name="pension")
        tag.delete()
        tag = Tag.nodes.get(name='income')
        tag.delete()
        tag = Tag.nodes.get(name="foreign_policy")
        tag.delete()

    def test_create_non_existent_tags(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        tags = ['hello_world_this_is_fake']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['tags'], [])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={"object_uuid": self.question.object_uuid})
        data = {}
        response = self.client.post(url, data, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response_data, response.data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.data, None)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_content(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.content, response.data['content'])

    def test_get_content_cached(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.content, response.data['content'])
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.content, response.data['content'])

    def test_get_title(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.title, response.data['title'])

    def test_update_title(self):
        self.client.force_authenticate(user=self.user)
        title = str(uuid1())
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        data = {
            "title": title
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.data['title'], title)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Question.get(self.question.object_uuid).title, title)

    def test_update_tags(self):
        self.client.force_authenticate(user=self.user)
        message = 'Sorry you cannot add or change tags after the ' \
                  'creation of a Question. We tie Reputation and' \
                  " search tightly to these values and don't want " \
                  "to confuse users with changes to them."
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        data = {
            "tags": ['fiscal', 'taxes']
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.data['tags'], [message])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_title_with_solution(self):
        self.client.force_authenticate(user=self.user)
        title = str(uuid1())
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        data = {
            "title": title
        }
        solution = Solution(content='this is fake content',
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.question.solutions.connect(solution)
        solution.solution_to.connect(self.question)
        self.pleb.solutions.connect(solution)
        response = self.client.patch(url, data, format='json')
        solution.solution_to.disconnect(self.question)
        self.question.solutions.disconnect(solution)
        self.pleb.solutions.disconnect(solution)
        solution.delete()
        self.assertEqual(response.data['title'],
                         ['Cannot edit Title when there have already '
                          'been solutions provided'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status_code'],
                         status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Question.get(self.question.object_uuid).title,
                         self.title)

    def test_update_content(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question. A new update to the content"
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        data = {
            "content": content
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.data['content'], content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Question.get(self.question.object_uuid).content, content)

    def test_get_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual('test_test',
                         response.data['profile'])

    def test_get_rendered(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?html=true" % reverse(
            'question-detail',
            kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("html" in response.data)
        self.assertTrue("ids" in response.data)
        self.assertTrue("solution_count" in response.data)

    def test_list_rendered(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-render')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("html" in response.data['results'])
        self.assertTrue("ids" in response.data['results'])

    def test_get_solutions_expedited(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?expedite=true" % reverse(
            'question-detail',
            kwargs={'object_uuid': self.question.object_uuid})
        solution = Solution(content='this is fake content',
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.question.solutions.connect(solution)
        solution.solution_to.connect(self.question)
        self.pleb.solutions.connect(solution)
        response = self.client.get(url, format='json')
        solution.solution_to.disconnect(self.question)
        self.question.solutions.disconnect(solution)
        self.pleb.solutions.disconnect(solution)
        solution.delete()

        self.assertEqual([], response.data['solutions'])

    def test_get_solutions_expanded(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?expand=true" % reverse(
            'question-detail',
            kwargs={'object_uuid': self.question.object_uuid})
        solution = Solution(content='this is fake content',
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.question.solutions.connect(solution)
        solution.solution_to.connect(self.question)
        self.pleb.solutions.connect(solution)
        response = self.client.get(url, format='json')
        solution.solution_to.disconnect(self.question)
        self.question.solutions.disconnect(solution)
        self.pleb.solutions.disconnect(solution)
        solution.delete()
        self.assertEqual(len(response.data['solutions']), 1)
        self.assertEqual(response.data['solutions'][0]['object_uuid'],
                         solution.object_uuid)

    def test_get_solutions_hyperlinked(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?relations=hyperlinked" % reverse(
            'question-detail',
            kwargs={'object_uuid': self.question.object_uuid})
        solution = Solution(content='this is fake content',
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.question.solutions.connect(solution)
        solution.solution_to.connect(self.question)
        self.pleb.solutions.connect(solution)
        response = self.client.get(url, format='json')
        solution.solution_to.disconnect(self.question)
        self.question.solutions.disconnect(solution)
        self.pleb.solutions.disconnect(solution)
        solution.delete()
        self.assertEqual(len(response.data['solutions']), 1)
        self.assertEqual(response.data['solutions'][0],
                         'http://testserver/v1/solutions/%s/' %
                         solution.object_uuid)

    def test_get_view_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['view_count'])

    def test_get_object_uuid(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.object_uuid,
                         response.data['object_uuid'])

    def test_get_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.object_uuid, response.data['id'])

    def test_last_edited_on(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.last_edited_on,
                         parser.parse(response.data['last_edited_on']))

    def test_get_created(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(self.question.created,
                         parser.parse(response.data['created']))

    def test_get_vote_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(None, response.data['vote_type'])

    def test_get_downvotes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['downvotes'])

    def test_get_upvotes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['upvotes'])

    def test_get_url(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual("http://testserver/conversations/%s/" %
                         self.question.object_uuid, response.data['url'])

    def test_get_vote_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(0, response.data['vote_count'])

    def test_get_flagged_by(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual([], response.data['flagged_by'])

    def test_get_href(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual("http://testserver/v1/questions/%s/" %
                         self.question.object_uuid, response.data['href'])

    def test_get_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual('question', response.data['type'])

    def test_get_list(self):
        for question in Question.nodes.all():
            question.delete()
        question = Question(title=str(uuid1()), content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(question)
        self.client.force_authenticate(user=self.user)
        url = reverse('question-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(4, len(response.data))
        self.assertEqual(1, len(response.data['results']))

    def test_list_tagged_as(self):
        for question in Question.nodes.all():
            question.delete()
        tag = Tag.nodes.get(name='fiscal')
        question = Question(title=str(uuid1()), content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(question)
        question.tags.connect(tag)
        self.client.force_authenticate(user=self.user)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&tagged_as=fiscal"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['tags'][0], 'fiscal')

    def test_list_tagged_as_non_core(self):
        for question in Question.nodes.all():
            question.delete()
        tag = Tag.nodes.get(name='taxes')
        question = Question(title=str(uuid1()), content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(question)
        question.tags.connect(tag)
        self.client.force_authenticate(user=self.user)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&tagged_as=taxes"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['tags'][0], 'taxes')

    def test_list_most_recent(self):
        for question in Question.nodes.all():
            question.delete()
        self.client.force_authenticate(user=self.user)
        question = Question(title=str(uuid1()), content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(question)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&sort_by=-created"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_least_recent(self):
        for question in Question.nodes.all():
            question.delete()
        self.client.force_authenticate(user=self.user)
        question = Question(title=str(uuid1()), content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(question)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&sort_by=created"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_vote_count(self):
        for question in Question.nodes.all():
            question.delete()
        self.client.force_authenticate(user=self.user)
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        self.pleb.questions.connect(question)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&sort_by=vote_count"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
