#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
import requests_mock
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework.test import APIRequestFactory
from rest_framework import status

from neomodel import db

from sagebrew.sb_registration.utils import create_user_util_test

from sagebrew.sb_questions.neo_models import Question

from sagebrew.sb_locations.utils import (
    parse_google_places, google_maps_query, connect_related_element,
    break_out_structure)
from sagebrew.sb_locations.neo_models import Location

springfield_data = [
    {
        'long_name': 'Springfield',
        'short_name': 'Springfield',
        'types': [
            'locality',
            'political'
        ],
    },
    {
        'long_name': 'Lee',
        'types': ['administrative_area_level_3', 'political'],
        'short_name': 'Lee'
    },
    {
        'long_name': 'Fairfax County',
        'types': [u'administrative_area_level_2', u'political'],
        'short_name': u'Fairfax County'
    },
    {
        'long_name': 'Virginia',
        'types': ['administrative_area_level_1', 'political'],
        'short_name': 'VA'
    },
    {
        'long_name': 'United States',
        'types': [u'country', u'political'],
        'short_name': u'US'
    }
]

wixom_data = {
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
    "adr_address": "<span class=\"locality\">Wixom</span>, "
                   "<span class=\"region\">MI</span>, "
                   "<span class=\"country-name\">USA</span>",
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
    "icon": "https://maps.gstatic.com/mapfiles/place_api/icons/geocode-71.png",
    "id": "20c67ea90c3088cc7d5fdd08dc7ccd170559a4fe",
    "name": "Wixom",
    "place_id": "ChIJ7xtMYSCmJIgRZBZBy5uZHl8",
    "reference": "CnRrAAAAd8ZPXfASBM6FFtdy7mckkorluFIIsJlBesOwOUtRqhIOhWPZJ"
                 "i8ul4sx8pozfeSSMYidyRbS37IkNcMJ2e76UsBnvrpWr-wRMKo-jfzCrJu"
                 "YQIxQ_1j40TTd_cZSMgQXVQgnqn940GYDuYTbpNT8thIQYBVqsZV4thkz"
                 "ZT90o9E0DBoUrELXmJ3GdZlCgHjdowsRZlQIDkk",
    "scope": "GOOGLE",
    "types": [
        "locality",
        "political"
    ],
    "url": "https://maps.google.com/?q=Wixom,+MI,+USA&ftid=0x8824a620614c1b"
           "ef:0x5f1e999bcb411664",
    "vicinity": "Wixom",
    "html_attributions": []
}


quebec_data = {
    "address_components": [
        {
            "long_name": "Québec",
            "short_name": "QC",
            "types": [
                "administrative_area_level_1",
                "political"
            ]
        },
        {
            "long_name": "Canada",
            "short_name": "CA",
            "types": [
                "country",
                "political"
            ]
        }
    ],
    "adr_address": "<span class=\"region\">Québec</span>, "
                   "<span class=\"country-name\">Canada</span>",
    "formatted_address": "Québec, Canada",
    "geometry": {
        "location": {},
        "viewport": {
            "O": {
                "O": 44.991467,
                "j": 62.5830552
            },
            "j": {
                "j": -79.76233709999997,
                "O": -57.10548589999996
            }
        }
    },
    "icon": "https://maps.gstatic.com/mapfiles/place_api/icons/geocode-71.png",
    "id": "a6cfab71073c170d9197ba86d6eb730d811d7158",
    "name": "Québec",
    "place_id": "ChIJoajRnzS1WEwRIABNrq0MBAE",
    "reference": "CnRsAAAA5-kHrOgEe2xlAPBuOYC0UwcOOQlxC7L0Gfwy7yIGeXb3c1YCm"
                 "HV4khN4RyG6fshyRyN_6CGFtHmwcwH70oxnt6Z0Hc16Np2X7VPnCACL20pY"
                 "a0q_UhtjXkaMDd_BUXvlHM9vR7TTmdUzx0VqCT3fFBIQLpscT9JZAKVt0s"
                 "41D_Km9xoUQb39do-5AjgRNPOko9JCnMtvE_4",
    "scope": "GOOGLE",
    "types": [
        "administrative_area_level_1",
        "political"
    ],
    "url": "https://maps.google.com/?q=Qu%C3%A9bec,+Canada&ftid=0x4c58b534"
           "9fd1a8a1:0x1040cadae4d0020",
    "html_attributions": []
}

us_data = {
    "address_components": [
        {
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
        }
    ],
    "adr_address": "<span class=\"country-name\">United States</span>",
    "formatted_address": "United States",
    "geometry": {
        "location": {},
        "viewport": {
            "O": {
                "O": 25.82,
                "j": 49.38
            },
            "j": {
                "j": -124.38999999999999,
                "O": -66.94
            }
        }
    },
    "icon": "https://maps.gstatic.com/mapfiles/place_api/icons/geocode-71.png",
    "id": "88564d30369b045e767b90442f46a1245864c58f",
    "name": "United States",
    "place_id": "ChIJCzYy5IS16lQRQrfeQ5K5Oxw",
    "reference": "CnRqAAAAYE4AsIIW_B_SVCIX1kSR0qsmcmEwLpupJTYeZhAfcKM"
                 "jiAmiW_nq-akQuceVCkLUdm5r9xTgM1P-y7eIVj34KmkbB2sv66R"
                 "do2Ku3nHVtI7Hlat0DpxVe0ZMcu1nijp3ZJe4m3azO_-dug8t4F5"
                 "g7RIQmtVbTdQtZgrQkph00SS-zxoUqMUuPKRf4m274r_LK4wM_OG2d4E",
    "scope": "GOOGLE",
    "types": [
        "country",
        "political"
    ],
    "url": "https://maps.google.com/?q=United+States&ftid=0x54eab584e4323"
           "60b:0x1c3bb99243deb742",
    "html_attributions": []
}


wixom_without_state_data = {
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
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
        }
    ],
    "adr_address": "<span class=\"locality\">Wixom</span>, "
                   "<span class=\"region\">MI</span>, "
                   "<span class=\"country-name\">USA</span>",
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
    "icon": "https://maps.gstatic.com/mapfiles/place_api/icons/geocode-71.png",
    "id": "20c67ea90c3088cc7d5fdd08dc7ccd170559a4fe",
    "name": "Wixom",
    "place_id": "ChIJ7xtMYSCmJIgRZBZBy5uZHl8",
    "reference": "CnRrAAAAd8ZPXfASBM6FFtdy7mckkorluFIIsJlBesOwOUtRqhIOhWPZJ"
                 "i8ul4sx8pozfeSSMYidyRbS37IkNcMJ2e76UsBnvrpWr-wRMKo-jfzCrJu"
                 "YQIxQ_1j40TTd_cZSMgQXVQgnqn940GYDuYTbpNT8thIQYBVqsZV4thkz"
                 "ZT90o9E0DBoUrELXmJ3GdZlCgHjdowsRZlQIDkk",
    "scope": "GOOGLE",
    "types": [
        "locality",
        "political"
    ],
    "url": "https://maps.google.com/?q=Wixom,+MI,+USA&ftid=0x8824a620614c1b"
           "ef:0x5f1e999bcb411664",
    "vicinity": "Wixom",
    "html_attributions": []
}


wixom_server_response = {
    "status": "OK",
    "html_attributions": [],
    "result": {
        "name": "Wixom",
        "reference": "CnRrAAAAF-JKA0ODb3Ew7iVtWAdgzzhwh2eksj94qI"
                     "RRFkUgdL99cqVhGWqyCj9zxDGvjEcXGtWtqAPMyko4lh"
                     "JFu8S27aWHVWMdwWP9bCw-q0OCEEbkwaWdCmgGm907Nly4"
                     "W3Cqf6B4XReTetE8caCK3tX2KhIQ_Iw9OY9Zu8jQZlDSnDRX"
                     "NRoUVzGc0rYpAs2gRzYS_u8JmLgxbos",
        "geometry": {
            "location": {
                "lat": 42.5247555,
                "lng": -83.5363268
            },
            "viewport": {
                "northeast": {
                    "lat": 42.55855589999999,
                    "lng": -83.507566
                },
                "southwest": {
                    "lat": 42.493165,
                    "lng": -83.558674
                }
            }
        },
        "adr_address": '<span class="locality">Wixom</span>, '
                       '<span class="region">MI</span>, '
                       '<span class="country-name">USA</span>',
        "place_id": "ChIJ7xtMYSCmJIgRZBZBy5uZHl8",
        "vicinity": "Wixom",
        "url": "https://maps.google.com/?q=Wixom,+MI,+USA&ftid="
               "0x8824a620614c1bef:0x5f1e999bcb411664",
        "scope": "GOOGLE",
        "address_components": [
            {
                "long_name": "Wixom",
                "types": [
                    "locality",
                    "political"
                ],
                "short_name": "Wixom"
            },
            {
                "long_name": "Oakland County",
                "types": [
                    "administrative_area_level_2",
                    "political"
                ],
                "short_name": "Oakland County"
            },
            {
                "long_name": "Michigan",
                "types": [
                    "administrative_area_level_1",
                    "political"
                ],
                "short_name": "MI"
            },
            {
                "long_name": "United States",
                "types": [
                    "country",
                    "political"
                ],
                "short_name": "US"
            }
        ],
        "formatted_address": "Wixom, MI, USA",
        "id": "20c67ea90c3088cc7d5fdd08dc7ccd170559a4fe",
        "types": [
            "locality",
            "political"
        ],
        "icon": "https://maps.gstatic.com/mapfiles/place_api"
                "/icons/geocode-71.png"
    }
}


class TestGooglePlaces(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def test_google_places_city(self):
        query = 'MATCH (a:Location) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        location = parse_google_places(wixom_data['address_components'],
                                       wixom_data['place_id'])

        self.assertEqual(location.name, "Wixom")
        res, _ = db.cypher_query('MATCH (a:Location '
                                 '{name: "Michigan"}) RETURN a')
        state = Location.inflate(res[0][0])
        res, _ = db.cypher_query('MATCH (a:Location '
                                 '{name: "United States of America"}) RETURN a')
        country = Location.inflate(res[0][0])
        self.assertTrue(state in location.encompassed_by)
        self.assertTrue(location in state.encompasses)

        self.assertTrue(country in state.encompassed_by)
        self.assertTrue(state in country.encompasses)

    @requests_mock.mock()
    def test_google_places_city_without_state(self, m):
        query = 'MATCH (a:Location) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        url = "https://maps.googleapis.com/maps/api/" \
              "place/details/json?placeid=%s&key=%s" % (
                  wixom_without_state_data['place_id'],
                  settings.GOOGLE_MAPS_API_SERVER)
        m.get(url, json=wixom_server_response, status_code=status.HTTP_200_OK)

        location = parse_google_places(
            wixom_without_state_data['address_components'],
            wixom_without_state_data['place_id'])

        self.assertEqual(location.name, "Wixom")
        res, _ = db.cypher_query('MATCH (a:Location '
                                 '{name: "Michigan"}) RETURN a')
        state = Location.inflate(res[0][0])
        res, _ = db.cypher_query('MATCH (a:Location '
                                 '{name: "United States of America"}) RETURN a')
        country = Location.inflate(res[0][0])
        self.assertTrue(state in location.encompassed_by)
        self.assertTrue(location in state.encompasses)

        self.assertTrue(country in state.encompassed_by)
        self.assertTrue(state in country.encompasses)

    def test_google_places_state(self):
        query = 'MATCH (a:Location) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        location = parse_google_places(quebec_data['address_components'],
                                       quebec_data['place_id'])

        self.assertEqual(location.name, "Quebec")
        res, _ = db.cypher_query('MATCH (a:Location '
                                 '{name: "Canada"}) RETURN a')
        country = Location.inflate(res[0][0])

        self.assertTrue(country in location.encompassed_by)
        self.assertTrue(location in country.encompasses)

    def test_google_places_country(self):
        query = 'MATCH (a:Location) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        location = parse_google_places(us_data['address_components'],
                                       us_data['place_id'])

        self.assertEqual(location.name, "United States of America")
        self.assertIsInstance(location, Location)

    def test_google_places_country_already_exists(self):
        query = 'MATCH (a:Location) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        old_location = Location(name="United States of America").save()
        location = parse_google_places(us_data['address_components'],
                                       us_data['place_id'])

        self.assertEqual(location.name, "United States of America")
        self.assertIsInstance(location, Location)
        self.assertEqual(old_location.object_uuid, location.object_uuid)

    def test_google_places_city_already_exists(self):
        query = 'MATCH (a:Location) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        old_country = Location(name="United States of America").save()
        old_state = Location(name="Michigan").save()
        old_city = Location(name="Wixom").save()
        old_country.encompasses.connect(old_state)
        old_state.encompassed_by.connect(old_country)
        old_state.encompasses.connect(old_city)
        old_city.encompassed_by.connect(old_state)

        location = parse_google_places(wixom_data['address_components'],
                                       wixom_data['place_id'])

        self.assertEqual(location.name, "Wixom")
        self.assertIsInstance(location, Location)
        self.assertEqual(old_city.object_uuid, location.object_uuid)

        self.assertTrue(old_state in location.encompassed_by)
        self.assertTrue(location in old_state.encompasses)

    def test_google_places_query(self):
        response = google_maps_query(wixom_data['place_id'])
        self.assertEqual(break_out_structure(
            wixom_server_response['result']['address_components']), response)

    def test_break_out_structure_server_city(self):
        structure = break_out_structure(wixom_data['address_components'])
        country = wixom_data['address_components'][3]
        country['long_name'] = "United States of America"
        state = wixom_data['address_components'][2]
        city = wixom_data['address_components'][0]
        self.assertEqual(country, structure[0])
        self.assertEqual(state, structure[1])
        self.assertEqual(city, structure[2])

    def test_break_out_structure_server_state(self):
        structure = break_out_structure(quebec_data['address_components'])
        country = quebec_data['address_components'][1]
        state = quebec_data['address_components'][0]
        self.assertEqual(country, structure[0])
        self.assertEqual(state, structure[1])
        self.assertIsNone(structure[2])

    def test_break_out_structure_server_country(self):
        structure = break_out_structure(us_data['address_components'])
        country = us_data['address_components'][0]
        self.assertEqual(country, structure[0])
        self.assertIsNone(structure[1])
        self.assertIsNone(structure[2])

    def test_break_out_structure_locality_and_admin_level_3(self):
        structure = break_out_structure(springfield_data)
        country = springfield_data[4]
        state = springfield_data[3]
        locality = springfield_data[0]
        self.assertEqual(country, structure[0])
        self.assertEqual(structure[1], state)
        self.assertEqual(structure[2], locality)

    def test_connect_related_element(self):
        cache.clear()
        query = 'MATCH (a:Question) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        question = Question(title="Hello this is my question",
                            content="This is content",
                            external_location_id=wixom_data['place_id'],
                            owner_username=self.pleb.username).save()
        location = parse_google_places(wixom_data['address_components'],
                                       wixom_data['place_id'])
        connect_related_element(location, wixom_data['place_id'])

        self.assertTrue(location in question.focus_location)

    def test_connect_no_related_element(self):
        cache.clear()
        query = 'MATCH (a:Question) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        question = Question(title="Hello this is my question",
                            content="This is content",
                            owner_username=self.pleb.username).save()
        location = parse_google_places(wixom_data['address_components'],
                                       wixom_data['place_id'])
        connected = connect_related_element(location, wixom_data['place_id'])
        self.assertIsNone(connected)
        question.delete()
