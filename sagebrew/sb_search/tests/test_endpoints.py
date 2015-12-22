import time
import pytz
import stripe
from uuid import uuid1
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db
from elasticsearch import Elasticsearch

from sb_privileges.neo_models import SBAction, Privilege
from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question
from sb_questions.serializers import QuestionSerializerNeo
from sb_locations.neo_models import Location
from sb_missions.neo_models import Mission

from sb_quests.neo_models import Quest, Position


class SearchEndpointTests(APITestCase):
    def setUp(self):
        query = "match (n)-[r]-() delete n,r"
        db.cypher_query(query)
        self.unit_under_test_name = 'quest'
        self.email = "success@simulator.amazonses.com"
        self.email2 = "success2@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.pleb2 = create_user_util_test(self.email2)
        self.user = User.objects.get(email=self.email)
        self.user2 = User.objects.get(email=self.email2)
        for camp in self.pleb.campaign.all():
            camp.delete()
        self.url = "http://testserver"
        self.quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        self.quest.editors.connect(self.pleb)
        self.quest.moderators.connect(self.pleb)
        cache.clear()
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
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

    def test_unauthorized(self):
        url = reverse('search-list')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_returns_expected(self):
        self.client.force_authenticate(user=self.user)
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        question1 = Question(object_uuid=str(uuid1()),
                             title=self.q1dict['title'],
                             content=self.q1dict['question_content'],
                             is_closed=False, solution_count=0,
                             last_edited_on=datetime.now(pytz.utc),
                             upvotes=0,
                             downvotes=0,
                             created=datetime.now(pytz.utc))
        question1.save()
        question1.owned_by.connect(self.pleb)
        index_res = es.index(index='full-search-base',
                             doc_type='question',
                             body=QuestionSerializerNeo(question1).data)
        self.assertTrue(index_res['created'])
        time.sleep(2)
        url = reverse('search-list') + "?query=battery-powered"
        response = self.client.get(url, format='json')
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertContains(response, question1.object_uuid,
                            status_code=status.HTTP_200_OK)

    def test_
