from django.test.testcases import TestCase

from neomodel import DoesNotExist, MultipleNodesReturned, db

from sb_locations.neo_models import Location

from sb_address.neo_models import Address


class TestAddress(TestCase):

    def setUp(self):
        self.address = Address(city="Wixom", state="MI").save()
        try:
            Location.nodes.get(name="Wixom").delete()
        except (Location.DoesNotExist, DoesNotExist):
            pass
        except MultipleNodesReturned:
            query = 'MATCH (a:Location {name:"Wixom"}) RETURN a'
            res, _ = db.cypher_query(query)
            for location in res[0]:
                Location.inflate(location).delete()
        try:
            self.state = Location.nodes.get(name="Michigan")
        except MultipleNodesReturned:
            query = 'MATCH (a:Location {name:"Michigan"}) RETURN a'
            res, _ = db.cypher_query(query)
            for location in res[0]:
                Location.inflate(location).delete()
        except (Location.DoesNotExist, DoesNotExist):
            self.state = Location(name="Michigan").save()

    def test_set_encompassing_no_nodes(self):
        res = self.address.set_encompassing()
        city = Location.nodes.get(name="Wixom")
        self.assertTrue(res.encompassed_by.is_connected(city))
        city.delete()

    def test_set_encompassing_city_exists(self):
        city = Location(name="Wixom").save()
        city.encompassed_by.connect(self.state)
        self.state.encompasses.connect(city)
        res = self.address.set_encompassing()
        self.assertTrue(res.encompassed_by.is_connected(city))
        city.delete()

    def test_multiple_cities_same_name(self):
        address = Address(city="Redford", state="Michigan").save()
        city = Location(name="Redford").save()
        city2 = Location(name="Redford").save()
        try:
            new_state = Location.nodes.get(name="Washington")
        except (Location.DoesNotExist, DoesNotExist):
            new_state = Location(name="Washington").save()
        self.state.encompasses.connect(city)
        city.encompassed_by.connect(self.state)
        city2.encompassed_by.connect(new_state)

        new_state.encompasses.connect(city2)
        res = address.set_encompassing()
        self.assertTrue(res.encompassed_by.is_connected(city))
        city.delete()
        city2.delete()
        address.delete()
