import time
from uuid import uuid1
from StringIO import StringIO

from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.core.cache import cache

from neomodel import db

from sb_registration.utils import create_user_util_test
from sb_missions.neo_models import Mission
from sb_quests.neo_models import Quest

from plebs.context_processors import request_profile


class RequestProfileTests(TestCase):

    def setUp(self):
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        db.cypher_query(query)
        cache.clear()
        self.factory = RequestFactory()
        self.email = "success@simulator.amazonses.com"
        self.password = "testpassword"
        res = create_user_util_test(self.email, task=True)
        while not res['task_id'].ready():
            time.sleep(.1)
        self.pleb = res['pleb']
        self.user = res['user']
        self.username = self.pleb.username
        self.pleb.email_verified = True
        self.pleb.save()

    def test_authenticated(self):
        request = self.factory.get(
            reverse('profile_page',
                    kwargs={"pleb_username": self.pleb.username}))
        request.user = self.user
        mission = Mission(owner_username=self.pleb.username,
                          title=str(uuid1()),
                          focus_name="advocacy",
                          location_name="11").save()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        quest.missions.connect(mission)
        quest.owner.connect(self.pleb)
        quest.editors.connect(self.pleb)
        quest.moderators.connect(self.pleb)
        res = request_profile(request)
        self.assertEqual(res['request_profile']['username'], self.user.username)

    def test_mission_in_path(self):
        request = self.factory.get("missions/select/")
        request.user = self.user
        mission = Mission(owner_username=self.pleb.username,
                          title=str(uuid1()),
                          focus_name="advocacy",
                          location_name="11").save()
        quest = Quest(
            about='Test Bio', owner_username=self.pleb.username).save()
        quest.missions.connect(mission)
        quest.owner.connect(self.pleb)
        quest.editors.connect(self.pleb)
        quest.moderators.connect(self.pleb)
        res = request_profile(request)
        self.assertEqual(res['request_profile']['username'],
                         self.user.username)

    def test_cypher_exception(self):
        request = self.factory.get("missions/select/")
        self.user.username = str(uuid1())
        request.user = self.user
        res = request_profile(request)
        expected = {
            "request_profile":
                {
                    "href": None,
                    "first_name": None,
                    "last_name": None,
                    "username": None,
                    "profile_pic": None,
                    "wallpaper_pic": None,
                    "reputation": None,
                    "privileges": [],
                    "actions": [],
                    "url": None
                }
        }
        self.assertEqual(res, expected)

    def test_unauthed(self):
        request = self.factory.get("missions/select/")
        request.user = AnonymousUser()
        res = request_profile(request)
        expected = {
            "request_profile":
                {
                    "href": None,
                    "first_name": None,
                    "last_name": None,
                    "username": None,
                    "profile_pic": None,
                    "wallpaper_pic": None,
                    "reputation": None,
                    "privileges": [],
                    "actions": [],
                    "url": None
                }
        }
        self.assertEqual(res, expected)

    def test_wsgi(self):
        request = WSGIRequest({
            "REQUEST_METHOD": "GET",
            "PATH_INFO": reverse("profile_page",
                                 kwargs={"pleb_username": self.pleb.username}),
            "wsgi.input": StringIO()
        })
        res = request_profile(request)
        expected = {
            "request_profile":
                {
                    "href": None,
                    "first_name": None,
                    "last_name": None,
                    "username": None,
                    "profile_pic": None,
                    "wallpaper_pic": None,
                    "reputation": None,
                    "privileges": [],
                    "actions": [],
                    "url": None
                }
        }
        self.assertEqual(res, expected)
