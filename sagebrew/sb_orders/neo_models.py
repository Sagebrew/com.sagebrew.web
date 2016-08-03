from neomodel import (db, RelationshipTo, IntegerProperty, BooleanProperty,
                      DateTimeProperty)

from api.neo_models import SBObject
from sb_base.neo_models import get_current_time


class Order(SBObject):
    # Whether or not the order has been processed by us. Updated when we
    # complete the order through the Council page.
    completed = BooleanProperty(default=False)
    total = IntegerProperty()

    # When the order was placed
    placed = DateTimeProperty(default=get_current_time)

    # relationships
    # Who placed the order.
    owner = RelationshipTo("plebs.neo_models.Pleb", "PLACED")

    def get_products(self):
        from sb_gifts.neo_models import Product
        query = 'MATCH (o:Order {object_uuid:"%s"})<-[:INCLUDED_IN]' \
                '-(p:Product) RETURN p'
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return [Product.inflate(row[0]) for row in res]
