import us
from uuid import uuid1

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from neomodel import db

from sagebrew.sb_address.neo_models import Address
from sagebrew.sb_locations.neo_models import Location
from sagebrew.sb_registration.utils import create_user_util_test
from sagebrew.sb_address.tasks import connect_to_state_districts


class TestCreateStateDistricts(TestCase):

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.email = "success@simulator.amazonses.com"
        self.pleb = create_user_util_test(self.email)
        self.user = User.objects.get(email=self.email)

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create_state_districts(self):
        mi = Location(name=us.states.lookup(
            "MI").name, sector="federal").save()
        address = Address(state="MI", latitude=42.532020,
                          longitude=-83.496500).save()
        lower = Location(name='38', sector='state_lower').save()
        upper = Location(name='15', sector='state_upper').save()
        mi.encompasses.connect(lower)
        lower.encompassed_by.connect(mi)
        mi.encompasses.connect(upper)
        upper.encompassed_by.connect(mi)
        res = connect_to_state_districts.apply_async(
            kwargs={'object_uuid': address.object_uuid})
        self.assertTrue(res.result)
        self.assertTrue(lower in address.encompassed_by)
        self.assertTrue(upper in address.encompassed_by)
        mi.delete()
        address.delete()
        upper.delete()
        lower.delete()

    def test_create_state_districts_already_exist(self):
        mi = Location(name=us.states.lookup(
            "MI").name, sector="federal").save()
        address = Address(state="MI", latitude=42.532020,
                          longitude=-83.496500).save()
        upper = Location(name="15", sector="state_upper").save()
        lower = Location(name="38", sector="state_lower").save()
        address.encompassed_by.connect(lower)
        address.encompassed_by.connect(upper)
        mi.encompasses.connect(upper)
        upper.encompassed_by.connect(mi)
        mi.encompasses.connect(lower)
        lower.encompassed_by.connect(mi)
        res = connect_to_state_districts.apply_async(
            kwargs={'object_uuid': address.object_uuid})
        self.assertTrue(res.result)
        query = 'MATCH (l:Location {name:"38", sector:"state_lower"}), ' \
                '(l2:Location {name:"15", sector:"state_upper"}) RETURN l, l2'
        res, _ = db.cypher_query(query)
        lower = Location.inflate(res[0].l)
        upper = Location.inflate(res[0].l2)
        self.assertTrue(lower in address.encompassed_by)
        self.assertTrue(upper in address.encompassed_by)
        res = connect_to_state_districts.apply_async(
            kwargs={'object_uuid': address.object_uuid})
        self.assertTrue(res.result)
        query = 'MATCH (l:Location {name:"38", sector:"state_lower"}), ' \
                '(l2:Location {name:"15", sector:"state_upper"}) RETURN l, l2'
        res, _ = db.cypher_query(query)
        self.assertEqual(len(res[0]), 2)  # assert only two nodes returned
        self.assertEqual(lower, Location.inflate(res[0].l))
        # assert only one lower node
        self.assertEqual(upper, Location.inflate(res[0].l2))
        # assert only one upper node
        mi.delete()
        address.delete()
        upper.delete()
        lower.delete()

    def test_address_doesnt_exist(self):
        res = connect_to_state_districts.apply_async(
            kwargs={"object_uuid": str(uuid1())})
        self.assertIsInstance(res.result, Exception)

    def test_address_has_no_lat_long(self):
        mi = Location(name=us.states.lookup(
            "MI").name, sector="federal").save()
        address = Address(state="MI").save()
        res = connect_to_state_districts.apply_async(
            kwargs={'object_uuid': address.object_uuid})
        self.assertFalse(res.result)
        mi.delete()
        address.delete()

    def test_address_has_lat_long_outside_usa(self):
        mi = Location(name=us.states.lookup(
            "MI").name, sector="federal").save()
        # lat/long of Greenwich UK
        address = Address(state="MI", latitude=51.4800,
                          longitude=0.0000).save()
        res = connect_to_state_districts.apply_async(
            kwargs={'object_uuid': address.object_uuid})
        self.assertTrue(res.result)
        mi.delete()
        address.delete()
