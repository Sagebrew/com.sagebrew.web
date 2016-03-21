import pytz
import time
from uuid import uuid1
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from neomodel import UniqueProperty
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError

from plebs.serializers import PlebSerializerNeo
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question
from sb_questions.serializers import QuestionSerializerNeo
from sb_missions.neo_models import Mission
from sb_missions.serializers import MissionSerializer
from sb_quests.neo_models import Quest
from sb_quests.serializers import QuestSerializer


class SearchEndpointTests(APITestCase):

    def setUp(self):
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        cache.clear()
        self.q1dict = {'title': 'Are current battery-powered '
                                'cars really more eco-friendly '
                                'than cars that run '
                                'off fossil fuels?',
                       'question_content': 'There have been mixed reviews'
                                           ' as to whether or not '
                                           'battery-powered cars are '
                                           'actually more eco-friendly, '
                                           'as they claim to be. On one '
                                           'side of the equation, battery'
                                           ' powered cars give off no '
                                           'fuel emissions, meaning no '
                                           'carbon dioxide or other '
                                           'greenhouse gasses that have '
                                           'been shown to negatively '
                                           'impact the balance of the '
                                           'environment. On the other '
                                           'side, the process by which '
                                           'electric cars are made, in '
                                           'addition to the electricity '
                                           'needed to power them, are '
                                           'both heavy proponents of '
                                           'greenhouse gas emissions. '}
        self.q2dict = {'title': 'How can we reduce the amount of'
                                ' NO2 pollution in the '
                                'atmosphere?',
                       'question_content': 'NO2 is a greenhouse gas 300 '
                                           'times more harmful to the '
                                           'environment than CO2, and the'
                                           ' levels of NO2 in the '
                                           'environment are rising '
                                           'far above average atmospheric'
                                           ' fluctuation. What are some '
                                           'of the causes of this and '
                                           'what can we do to reduce the '
                                           'amount of NO2 being placed '
                                           'into the atmosphere? '}
        try:
            self.question = Question(object_uuid=str(uuid1()),
                                     title=self.q1dict['title'],
                                     content=self.q1dict['question_content'],
                                     is_closed=False, solution_count=0,
                                     last_edited_on=datetime.now(pytz.utc),
                                     upvotes=0,
                                     downvotes=0,
                                     created=datetime.now(pytz.utc)).save()
        except UniqueProperty:
            self.question = Question.nodes.get(title=self.q1dict['title'])
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        try:
            es.indices.create(index="full-search-base")
        except TransportError:
            pass

    def tearDown(self):
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        es.indices.delete(index="full-search-base")
        try:
            es.indices.create(index="full-search-base")
        except TransportError:
            pass

    def test_unauthorized(self):
        url = reverse('search-list')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_returns_expected(self):
        self.client.force_authenticate(user=self.user)
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        index_res = es.index(index='full-search-base',
                             doc_type='question',
                             body=QuestionSerializerNeo(self.question).data)
        time.sleep(1)
        self.assertTrue(index_res['created'])
        url = reverse('search-list') + "?query=battery-powered"
        response = self.client.get(url, format='json')
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertContains(response, self.question.object_uuid,
                            status_code=status.HTTP_200_OK)
        self.question.delete()

    def test_fuzzy(self):
        self.client.force_authenticate(user=self.user)
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        index_res = es.index(index='full-search-base',
                             doc_type='question',
                             body=QuestionSerializerNeo(self.question).data)
        time.sleep(1)
        self.assertTrue(index_res['created'])
        url = reverse('search-list') + "?query=battery-powed"
        response = self.client.get(url, format='json')
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertContains(response, self.question.object_uuid,
                            status_code=status.HTTP_200_OK)
        self.question.delete()

    def test_sloppy(self):
        self.client.force_authenticate(user=self.user)
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        index_res = es.index(index='full-search-base',
                             doc_type='question',
                             body=QuestionSerializerNeo(self.question).data)
        time.sleep(1)
        self.assertTrue(index_res['created'])
        url = reverse('search-list') + "?query=levels of"
        response = self.client.get(url, format='json')
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertContains(response, self.question.object_uuid,
                            status_code=status.HTTP_200_OK)
        self.question.delete()

    def test_filter(self):
        self.client.force_authenticate(user=self.user)
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        index_res = es.index(index='full-search-base',
                             doc_type='question',
                             body=QuestionSerializerNeo(self.question).data)
        time.sleep(1)
        self.assertTrue(index_res['created'])
        url = reverse('search-list') + "?query=battery-powered&" \
                                       "filter=conversations"
        response = self.client.get(url, format='json')
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertContains(response, self.question.object_uuid,
                            status_code=status.HTTP_200_OK)
        self.question.delete()

    def test_quest(self):
        self.client.force_authenticate(user=self.user)
        quest = Quest(owner_username=self.pleb.username,
                      first_name="Tyler", last_name="Wiersing").save()
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        index_res = es.index(index='full-search-base',
                             doc_type='quest',
                             body=QuestSerializer(quest).data)
        time.sleep(1)
        self.assertTrue(index_res['created'])
        url = reverse('search-list') + "?query=tyler&filter=quests"
        response = self.client.get(url, format='json')
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertContains(response, quest.object_uuid,
                            status_code=status.HTTP_200_OK)

    def test_mission(self):
        self.client.force_authenticate(user=self.user)
        mission = Mission(owner_username=self.pleb.username).save()
        quest = Quest(owner_username=self.pleb.username,
                      first_name="Tyler", last_name="Wiersing").save()
        quest.missions.connect(mission)
        cache.clear()
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        index_res = es.index(index='full-search-base',
                             doc_type='mission',
                             body=MissionSerializer(mission).data)
        time.sleep(1)
        self.assertTrue(index_res['created'])
        url = reverse('search-list') + "?query=test_test&filter=missions"
        response = self.client.get(url, format='json')
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertContains(response, mission.object_uuid,
                            status_code=status.HTTP_200_OK)

    def test_pleb(self):
        self.client.force_authenticate(user=self.user)
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        index_res = es.index(index='full-search-base',
                             doc_type='profile',
                             body=PlebSerializerNeo(self.pleb).data)
        time.sleep(1)
        self.assertTrue(index_res['created'])
        url = reverse('search-list') + "?query=test&filter=people"
        response = self.client.get(url, format='json')
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertContains(response, self.pleb.username,
                            status_code=status.HTTP_200_OK)

    def test_invalid_filter(self):
        self.client.force_authenticate(user=self.user)
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        index_res = es.index(index='full-search-base',
                             doc_type='question',
                             body=QuestionSerializerNeo(self.question).data)
        time.sleep(1)
        self.assertTrue(index_res['created'])
        url = reverse('search-list') + "?query=battery-powered&" \
                                       "filter=" + str(uuid1())
        response = self.client.get(url, format='json')

        self.assertContains(response, "We currently have limited support for "
                                      "filter operations.",
                            status_code=status.HTTP_400_BAD_REQUEST)
        self.question.delete()
