import time

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test
from sb_questions.neo_models import Question
from sb_locations.tasks import create_location_tree, connect_location_to_element

from sb_locations.neo_models import Location


class TestCreateLocationTreeTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.wixom = {
            "address_components": [
                {
                    "long_name": "Wixom",
                    "short_name": "Wixom",
                    "types": [
                        "locality",
                        "political"
                    ]
                },
                {
                    "long_name": "Oakland County",
                    "short_name": "Oakland County",
                    "types": [
                        "administrative_area_level_2",
                        "political"
                    ]
                },
                {
                    "long_name": "Michigan",
                    "short_name": "MI",
                    "types": [
                        "administrative_area_level_1",
                        "political"
                    ]
                },
                {
                    "long_name": "United States",
                    "short_name": "US",
                    "types": [
                        "country",
                        "political"
                    ]
                }
            ],
            "adr_address": "",
            "formatted_address": "Wixom, MI, USA",
            "geometry": {
                "location": {},
                "viewport": {
                    "O": {
                        "O": 42.493165,
                        "j": 42.55855589999999
                    },
                    "j": {
                        "j": -83.558674,
                        "O": -83.507566
                    }
                }
            },
            "icon": "https://maps.gstatic.com/mapfiles/"
                    "place_api/icons/geocode-71.png",
            "id": "20c67ea90c3088cc7d5fdd08dc7ccd170559a4fe",
            "name": "Wixom",
            "place_id": "ChIJ7xtMYSCmJIgRZBZBy5uZHl8",
            "reference": "Bnv9E0DBoUrELXmJ3GdZlCgHjdowsRZlQIDkk",
            "scope": "GOOGLE",
            "types": [
                "locality",
                "political"
            ],
            "url": "https://maps.google.com/"
                   "?q=Wixom,+MI,+USA&ftid="
                   "0x8824a620614c1bef:0x5f1e999bcb411664",
            "vicinity": "Wixom",
            "html_attributions": []
        }
        cache.set(self.wixom['place_id'], self.wixom)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_location_tree_with_cache_set(self):
        data = {
            'external_id': self.wixom['place_id']
        }
        res = create_location_tree.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        self.assertIsInstance(res.result, Location)

    def test_location_tree_without_cache(self):
        data = {
            'external_id': 'hello_world'
        }
        res = create_location_tree.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, KeyError)


class TestConnectLocationElementTask(TestCase):
    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        res = create_user_util_test(self.email, task=True)
        self.assertNotEqual(res, False)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.wixom = {
            "address_components": [
                {
                    "long_name": "Wixom",
                    "short_name": "Wixom",
                    "types": [
                        "locality",
                        "political"
                    ]
                },
                {
                    "long_name": "Oakland County",
                    "short_name": "Oakland County",
                    "types": [
                        "administrative_area_level_2",
                        "political"
                    ]
                },
                {
                    "long_name": "Michigan",
                    "short_name": "MI",
                    "types": [
                        "administrative_area_level_1",
                        "political"
                    ]
                },
                {
                    "long_name": "United States",
                    "short_name": "US",
                    "types": [
                        "country",
                        "political"
                    ]
                }
            ],
            "adr_address": "",
            "formatted_address": "Wixom, MI, USA",
            "geometry": {
                "location": {},
                "viewport": {
                    "O": {
                        "O": 42.493165,
                        "j": 42.55855589999999
                    },
                    "j": {
                        "j": -83.558674,
                        "O": -83.507566
                    }
                }
            },
            "icon": "https://maps.gstatic.com/mapfiles/"
                    "place_api/icons/geocode-71.png",
            "id": "20c67ea90c3088cc7d5fdd08dc7ccd170559a4fe",
            "name": "Wixom",
            "place_id": "ChIJ7xtMYSCmJIgRZBZBy5uZHl8",
            "reference": "Bnv9E0DBoUrELXmJ3GdZlCgHjdowsRZlQIDkk",
            "scope": "GOOGLE",
            "types": [
                "locality",
                "political"
            ],
            "url": "https://maps.google.com/"
                   "?q=Wixom,+MI,+USA&ftid="
                   "0x8824a620614c1bef:0x5f1e999bcb411664",
            "vicinity": "Wixom",
            "html_attributions": []
        }
        cache.set(self.wixom['place_id'], self.wixom)
        data = {
            'external_id': self.wixom['place_id']
        }
        res = create_location_tree.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.location = res.result

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_connect_with_existing_element(self):
        question = Question(title="Hello this is my question",
                            content="This is content",
                            external_location_id=self.wixom['place_id'],
                            owner_username=self.pleb.username).save()
        data = {
            'element_id': self.wixom['place_id'],
            'location': self.location
        }
        res = connect_location_to_element.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertTrue(res.result)
        self.assertIsInstance(res.result, Question)
        question.delete()

    def test_connect_without_question(self):
        data = {
            'element_id': self.wixom['place_id'],
            'location': self.location
        }
        res = connect_location_to_element.apply_async(kwargs=data)
        while not res.ready():
            time.sleep(1)
        self.assertIsInstance(res.result, KeyError)
