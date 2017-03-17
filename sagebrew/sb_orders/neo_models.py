from neomodel import (db, RelationshipTo, IntegerProperty, BooleanProperty,
                      DateTimeProperty, StringProperty)

from sagebrew.api.neo_models import SBObject
from sagebrew.sb_base.neo_models import get_current_time


class Order(SBObject):
    # Whether or not the Order has been processed by us. Updated when we
    # complete the order through the Council page.
    completed = BooleanProperty(default=False)
    # Whether or not the Order has been paid for.
    # Updated when the stripe payment completes
    paid = BooleanProperty(default=False)

    # Total cost of the Order in an int with cents being the las 2 digits
    total = IntegerProperty()

    stripe_charge_id = StringProperty()

    tracking_url = StringProperty()

    # When the order was placed
    placed = DateTimeProperty(default=get_current_time)
    owner_username = StringProperty()

    # relationships
    # Who placed the order.
    owner = RelationshipTo("sagebrew.plebs.neo_models.Pleb", "PLACED")
    mission = RelationshipTo(
        "sagebrew.sb_missions.neo_models.Mission", "GIFTED_TO")

    def get_products(self):
        from sagebrew.sb_gifts.neo_models import Product
        query = 'MATCH (o:Order {object_uuid:"%s"})<-[:INCLUDED_IN]' \
                '-(p:Product) RETURN p' % self.object_uuid
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Product.inflate(row[0]) for row in res]

    def get_mission(self):
        from sagebrew.sb_missions.neo_models import Mission
        query = 'MATCH (o:Order {object_uuid:"%s"})-[:GIFTED_TO]->' \
                '(m:Mission) RETURN m' % self.object_uuid
        res, _ = db.cypher_query(query)
        res = res[0] if res else None
        if res:
            return Mission.inflate(res[0][0])
        return None
