from uuid import uuid1
from dateutil import parser

from django.utils.text import slugify
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.management import call_command

from rest_framework import status, serializers
from rest_framework.test import APITestCase

from neomodel.exception import DoesNotExist
from neomodel import db

from sb_privileges.neo_models import Privilege
from sb_tags.neo_models import Tag
from sb_votes.utils import create_vote_relationship
from sb_questions.neo_models import Question
from sb_questions.serializers import QuestionSerializerNeo
from sb_solutions.neo_models import Solution
from sb_registration.utils import create_user_util_test


class QuestionEndpointTests(APITestCase):

    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        self.email2 = "bounces@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.pleb2 = create_user_util_test(self.email2)
        self.title = str(uuid1())
        self.question = Question(content="Hey I'm a question",
                                 title=self.title,
                                 owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)
        self.user = User.objects.get(email=self.email)
        self.user2 = User.objects.get(email=self.email2)
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

    def test_create_with_new_tags_no_rep(self):
        self.client.force_authenticate(user=self.user)
        self.pleb.reputation = 0
        self.pleb.save()
        cache.clear()
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        tag_name = 'non-existent tag'
        tags = ['taxes', tag_name]
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        query = 'MATCH (a:Tag {name: "%s"}) RETURN a' % slugify(tag_name)
        res, _ = db.cypher_query(query)
        self.assertIsNone(res.one)

    def test_create_with_new_tags_with_rep(self):
        self.client.force_authenticate(user=self.user)
        self.pleb.reputation = 1250
        self.pleb.save()
        cache.clear()
        tag_name = 'non-existent tag with more'
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = "This is a new question that doesn't have a title green"
        tags = ['taxes', tag_name]
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.pleb.reputation = 0
        self.pleb.save()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        query = 'MATCH (a:Tag {name: "%s"}) RETURN a' % slugify(tag_name)
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)
        query = 'MATCH (a:Tag {name: "%s"})<-[:TAGGED_AS]-' \
                '(question:Question {object_uuid: "%s"}) ' \
                'RETURN question' % (slugify(tag_name), response.data['id'])
        res, _ = db.cypher_query(query)
        self.assertIsNotNone(res.one)

    def test_create_with_h3_first(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        content = "<h3> hello world this is a h3 </h3><br>" \
                  "<h2> with a h2 after it </h2><br>" \
                  "<h3> another h3 </h3><br>" \
                  "and then some text"
        title = "This is a question that must be t is blue216666?"
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        html_content = '<h3 style="padding-top: 0; margin-top: 5px;"> ' \
                       'hello world this is a h3 </h3><br/><h2> with a ' \
                       'h2 after it </h2><br/><h3> another h3 </h3><br/>' \
                       'and then some text'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], html_content)
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)

    def test_create_with_h2_first(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        content = "<h2> hello world this is a h2 </h2><br>" \
                  "<h3> with a h3 after it </h3><br>" \
                  "<h2 another h2 </h2><br>" \
                  "and then some text"
        title = "This is a question that must be t is blue21222?"
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        html_content = '<h2 style="padding-top: 0; margin-top: 5px;"> ' \
                       'hello world this is a h2 </h2><br/><h3> with a h3 ' \
                       'after it </h3><br/><h2 another="" h2=""><br/>' \
                       'and then some text</h2>'
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], html_content)
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)

    def test_create_with_focus_area(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        url = reverse('question-list')
        data = {
            "content": "<p>%s</p>" % content,
            "title": str(uuid1()),
            "tags": ['taxes', 'environment'],
            "latitude": 42.5247555,
            "longitude": -83.53632679999998,
            "affected_area": "Wixom, MI, USA",
            "external_location_id": "ChIJ7xtMYSCmJIgRZBZBy5uZHl8"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        res, _ = db.cypher_query('MATCH (a:Question '
                                 '{object_uuid: "%s"}) RETURN a' %
                                 response.data['object_uuid'])
        question = Question.inflate(res.one)
        self.assertEqual(question.affected_area, "Wixom, MI, USA")
        self.assertEqual(question.content, data['content'])
        self.assertEqual(question.object_uuid, response.data['object_uuid'])

    def test_create_null_focus_area(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        url = reverse('question-list')
        data = {
            "content": "<p>%s</p>" % content,
            "title": str(uuid1()),
            "tags": ['taxes', 'environment'],
            "latitude": None,
            "longitude": None,
            "affected_area": None,
            "external_location_id": None
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        res, _ = db.cypher_query('MATCH (a:Question {object_uuid: '
                                 '"%s"}) RETURN a' %
                                 response.data['object_uuid'])
        question = Question.inflate(res.one)
        self.assertEqual(question.content, data['content'])

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

    def test_create_title_with_quotes(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = '"images/wallpaper_western.jpg""images/wallpaper_western.jpg' \
                '""images/wallpaper_western.jpg"'
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], title)

    def test_create_title_with_apostrophes(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = "'images/wallpaper_western.jpg''images/wallpaper_western.jpg'" \
                "''images/wallpaper_western.jpg'"
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], title)

    def test_create_content(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question."
        title = str(uuid1())
        tags = ['taxes', 'environment']
        url = reverse('question-list')
        data = {
            "content": "<p>%s</p>" % content,
            "title": title,
            "tags": tags
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data['content'], data['content'])

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
                         ['Ensure this field has no more than 120 characters.'])
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

    def test_update_focus_area(self):
        self.client.force_authenticate(user=self.user)
        cache.clear()
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        latitude = 42.537811
        longitude = -83.48104810000001
        affected_area = "Walled Lake, MI, USA"
        external_id = "ChIJCV7PpJGlJIgRkkwposHal-Q"
        data = {
            "latitude": latitude,
            "longitude": longitude,
            "affected_area": affected_area,
            "external_location_id": external_id
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res, _ = db.cypher_query('MATCH (a:Question '
                                 '{external_location_id: '
                                 '"ChIJCV7PpJGlJIgRkkwposHal-Q"}) RETURN a')
        question = Question.inflate(res.one)
        updated_question = Question.get(self.question.object_uuid)
        self.assertEqual(question.affected_area, "Walled Lake, MI, USA")
        self.assertEqual(question.latitude, 42.537811)
        self.assertEqual(question.object_uuid, response.data['object_uuid'])
        self.assertEqual(updated_question.latitude, latitude)
        self.assertEqual(updated_question.longitude, longitude)
        self.assertEqual(updated_question.affected_area, affected_area)
        self.assertEqual(updated_question.external_location_id, external_id)

    def test_update_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        title = str(uuid1())
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        data = {
            "title": title
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.data, ['Only the owner can edit this'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_no_request(self):
        serializer = QuestionSerializerNeo(data={
            "title": self.question.title
        }, instance=self.question, partial=True)
        serializer.is_valid()
        try:
            serializer.save()
            # We shouldn't be able to save unless is_valid has errors set.
            self.assertTrue(False)
        except serializers.ValidationError as e:
            self.assertEqual(e.detail, ['Cannot update without request'])

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

    def test_update_same_title(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        data = {
            "title": self.question.title
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.data['title'], self.question.title)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Question.get(self.question.object_uuid).title,
                         self.question.title)

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
        response = self.client.patch(url, data, format='json')
        self.question.solutions.disconnect(solution)
        solution.delete()
        self.assertEqual(response.data['title'],
                         ['Cannot edit when there have already been '
                          'solutions provided'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Question.get(self.question.object_uuid).title,
                         self.title)

    def test_update_content(self):
        self.client.force_authenticate(user=self.user)
        content = "This is the content to my question, it's a pretty good " \
                  "question. A new update to the content"
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        data = {
            "content": "<p>%s</p>" % content
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.data['content'], data['content'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('question-detail',
                      kwargs={'object_uuid': self.question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual('test_test', response.data['profile']['username'])

    def test_get_solutions_expedited(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?expedite=true" % reverse(
            'question-detail',
            kwargs={'object_uuid': self.question.object_uuid})
        solution = Solution(content='this is fake content',
                            owner_username=self.pleb.username).save()
        solution.owned_by.connect(self.pleb)
        self.question.solutions.connect(solution)
        response = self.client.get(url, format='json')
        self.question.solutions.disconnect(solution)
        solution.delete()

        self.assertEqual([], response.data['solutions'])

    def test_get_solutions_expanded(self):
        self.client.force_authenticate(user=self.user)
        url = "%s?expand=true" % reverse(
            'question-detail',
            kwargs={'object_uuid': self.question.object_uuid})
        solution = Solution(content='this is fake content',
                            owner_username=self.pleb.username,
                            parent_id=self.question.object_uuid).save()
        solution.owned_by.connect(self.pleb)
        self.question.solutions.connect(solution)
        response = self.client.get(url, format='json')
        self.question.solutions.disconnect(solution)
        solution.delete()
        self.assertEqual(len(response.data['solutions']), 1)
        self.assertEqual(response.data['solutions'][0]['object_uuid'],
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
        self.assertEqual("http://testserver/conversations/%s/%s/" %
                         (self.question.object_uuid,
                          slugify(self.question.title)),
                         response.data['url'])

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
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        question = Question(title=str(uuid1()), content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        self.client.force_authenticate(user=self.user)
        url = reverse('question-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(4, len(response.data))
        self.assertEqual(1, len(response.data['results']))

    def test_list_tagged_as(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        tag = Tag.nodes.get(name='fiscal')
        question = Question(title=str(uuid1()), content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        question.tags.connect(tag)
        self.client.force_authenticate(user=self.user)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&tagged_as=fiscal"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['tags'][0], 'fiscal')

    def test_list_tagged_as_non_core(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        tag = Tag.nodes.get(name='taxes')
        question = Question(title=str(uuid1()), content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        question.tags.connect(tag)
        self.client.force_authenticate(user=self.user)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&tagged_as=taxes"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['tags'][0], 'taxes')

    def test_list_most_recent(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        question = Question(title=str(uuid1()), content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&ordering=-created"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_most_recent_ordering(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        # Question 1
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb2.username).save()
        question.owned_by.connect(self.pleb2)
        # Question 2
        question2 = Question(title='test_title22', content='test_content22',
                             owner_username=self.pleb.username).save()
        question2.owned_by.connect(self.pleb)
        # Question 3
        question3 = Question(title='test_title33', content='test_content33',
                             owner_username=self.pleb.username).save()
        question3.owned_by.connect(self.pleb)
        # Question 4
        question4 = Question(title='test_title44', content='test_content44',
                             owner_username=self.pleb2.username).save()
        question4.owned_by.connect(self.pleb2)
        # Question 5
        question5 = Question(title='test_title55', content='test_content55',
                             owner_username=self.pleb.username).save()
        question5.owned_by.connect(self.pleb)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&ordering=-created"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['results'][0]['id'],
                         question5.object_uuid)
        self.assertEqual(response.data['results'][1]['id'],
                         question4.object_uuid)
        self.assertEqual(response.data['results'][2]['id'],
                         question3.object_uuid)
        self.assertEqual(response.data['results'][3]['id'],
                         question2.object_uuid)
        self.assertEqual(response.data['results'][4]['id'],
                         question.object_uuid)

    def test_list_least_recent(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        question = Question(title=str(uuid1()), content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&ordering=created"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_least_recent_ordering(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        # Question 1
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb2.username).save()
        question.owned_by.connect(self.pleb2)
        # Question 2
        question2 = Question(title='test_title22', content='test_content22',
                             owner_username=self.pleb.username).save()
        question2.owned_by.connect(self.pleb)
        # Question 3
        question3 = Question(title='test_title33', content='test_content33',
                             owner_username=self.pleb.username).save()
        question3.owned_by.connect(self.pleb)
        # Question 4
        question4 = Question(title='test_title44', content='test_content44',
                             owner_username=self.pleb2.username).save()
        question4.owned_by.connect(self.pleb2)
        # Question 5
        question5 = Question(title='test_title55', content='test_content55',
                             owner_username=self.pleb.username).save()
        question5.owned_by.connect(self.pleb)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&ordering=created"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['results'][0]['id'],
                         question.object_uuid)
        self.assertEqual(response.data['results'][1]['id'],
                         question2.object_uuid)
        self.assertEqual(response.data['results'][2]['id'],
                         question3.object_uuid)
        self.assertEqual(response.data['results'][3]['id'],
                         question4.object_uuid)
        self.assertEqual(response.data['results'][4]['id'],
                         question5.object_uuid)

    def test_list_vote_count(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&ordering=vote_count"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_vote_count_ordering(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        pleb3 = create_user_util_test("devon@sagebrew.com")
        # Question 1 Upvote 1
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        create_vote_relationship(question.object_uuid, self.pleb2.username,
                                 "true", "true")
        # Question 2 Downvote 1
        question2 = Question(title='test_title22', content='test_content22',
                             owner_username=self.pleb.username).save()

        question2.owned_by.connect(self.pleb)
        create_vote_relationship(question2.object_uuid, self.pleb2.username,
                                 "true", "false")
        # Question 3 No Votes
        question3 = Question(title='test_title33', content='test_content33',
                             owner_username=self.pleb.username).save()

        question3.owned_by.connect(self.pleb)
        # Question 4 Downvote 2
        question4 = Question(title='test_title44', content='test_content44',
                             owner_username=self.pleb.username).save()

        question4.owned_by.connect(self.pleb)
        create_vote_relationship(question4.object_uuid, self.pleb2.username,
                                 "true", "false")

        create_vote_relationship(question4.object_uuid, pleb3.username,
                                 "true", "false")
        # Question 5 Upvote 2
        question5 = Question(title='test_title55', content='test_content55',
                             owner_username=self.pleb.username).save()

        question5.owned_by.connect(self.pleb)
        create_vote_relationship(question5.object_uuid, self.pleb2.username,
                                 "true", "true")
        create_vote_relationship(question5.object_uuid, pleb3.username,
                                 "true", "true")
        url = reverse('question-list') + "?limit=5&offset=0&" \
                                         "expand=true&ordering=vote_count"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['results'][0]['id'],
                         question5.object_uuid)
        self.assertEqual(response.data['results'][1]['id'],
                         question.object_uuid)
        self.assertEqual(response.data['results'][2]['id'],
                         question3.object_uuid)
        self.assertEqual(response.data['results'][3]['id'],
                         question2.object_uuid)
        self.assertEqual(response.data['results'][4]['id'],
                         question4.object_uuid)


class SBBaseSerializerTests(APITestCase):
    # TODO This should be moved somewhere not tighly coupled to a give content
    # object.
    def setUp(self):
        self.unit_under_test_name = 'pleb'
        self.email = "success@simulator.amazonses.com"
        self.email2 = "bounces@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.pleb2 = create_user_util_test(self.email2)
        self.title = str(uuid1())
        self.question = Question(content="Hey I'm a question",
                                 title=self.title,
                                 owner_username=self.pleb.username).save()
        self.question.owned_by.connect(self.pleb)
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
        try:
            Privilege.nodes.get(name="flag")
        except(Privilege.DoesNotExist, DoesNotExist):
            call_command('create_privileges')

    def test_can_comment_own(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        for item in self.pleb.privileges.all():
            self.pleb.privileges.disconnect(item)
        cache.clear()
        url = reverse('question-detail',
                      kwargs={'object_uuid': question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['can_comment']['status'])
        self.assertIsNone(response.data['can_comment']['detail'])
        self.assertIsNone(response.data['can_comment']['short_detail'])

    def test_can_comment_other(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb2)
        privilege = Privilege.nodes.get(name="comment")
        self.pleb.privileges.connect(privilege)
        cache.clear()
        url = reverse('question-detail',
                      kwargs={'object_uuid': question.object_uuid})
        response = self.client.get(url, format='json')
        self.pleb.privileges.disconnect(privilege)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['can_comment']['status'])
        self.assertIsNone(response.data['can_comment']['detail'])
        self.assertIsNone(response.data['can_comment']['short_detail'])

    def test_cannot_comment_other(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb2.username).save()
        question.owned_by.connect(self.pleb2)
        for item in self.pleb.privileges.all():
            self.pleb.privileges.disconnect(item)
        cache.clear()
        url = reverse('question-detail',
                      kwargs={'object_uuid': question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['can_comment']['status'])
        self.assertEqual(response.data['can_comment']['detail'],
                         "You must have 20+ reputation to comment on "
                         "Conversation Cloud content.")
        self.assertEqual(response.data['can_comment']['short_detail'],
                         "Requirement: 20+ Reputation")

    def test_login_to_comment(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        url = reverse('question-detail',
                      kwargs={'object_uuid': question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['can_comment']['status'])
        self.assertEqual(response.data['can_comment']['detail'],
                         "You must be logged in to comment on content.")
        self.assertEqual(response.data['can_comment']['short_detail'],
                         "Signup To Comment")

    def test_is_not_owner(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb2.username).save()
        question.owned_by.connect(self.pleb2)
        for item in self.pleb.privileges.all():
            self.pleb.privileges.disconnect(item)
        cache.clear()
        url = reverse('question-detail',
                      kwargs={'object_uuid': question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_owner'])

    def test_can_flag(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb2.username).save()
        question.owned_by.connect(self.pleb2)
        privilege = Privilege.nodes.get(name="flag")
        self.pleb.privileges.connect(privilege)
        cache.clear()
        url = reverse('question-detail',
                      kwargs={'object_uuid': question.object_uuid})
        response = self.client.get(url, format='json')
        self.pleb.privileges.disconnect(privilege)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['can_flag']['status'])
        self.assertIsNone(response.data['can_flag']['detail'])
        self.assertIsNone(response.data['can_flag']['short_detail'])

    def test_login_to_flag(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        url = reverse('question-detail',
                      kwargs={'object_uuid': question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['can_flag']['status'])
        self.assertEqual(response.data['can_flag']['detail'],
                         "You must be logged in to flag content.")
        self.assertEqual(response.data['can_flag']['short_detail'],
                         "Signup To Flag")

    def test_can_not_flag(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb2.username).save()
        question.owned_by.connect(self.pleb2)
        for item in self.pleb.privileges.all():
            self.pleb.privileges.disconnect(item)
        cache.clear()
        url = reverse('question-detail',
                      kwargs={'object_uuid': question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['can_flag']['status'])
        self.assertEqual(response.data['can_flag']['detail'],
                         "You must have 50+ reputation to flag Conversation "
                         "Cloud content.")
        self.assertEqual(response.data['can_flag']['short_detail'],
                         "Requirement: 50+ Reputation")

    def test_can_not_flag_own(self):
        query = "MATCH (n:SBContent) OPTIONAL MATCH " \
                "(n:SBContent)-[r]-() DELETE n,r"
        res, _ = db.cypher_query(query)
        self.client.force_authenticate(user=self.user)
        question = Question(title='test_title', content='test_content',
                            owner_username=self.pleb.username).save()
        question.owned_by.connect(self.pleb)
        url = reverse('question-detail',
                      kwargs={'object_uuid': question.object_uuid})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['can_flag']['status'])
        self.assertEqual(response.data['can_flag']['detail'],
                         "You cannot flag your own content")
        self.assertEqual(response.data['can_flag']['short_detail'],
                         "Cannot Flag Own Content")
