from neomodel import (db, RelationshipTo, StringProperty, BooleanProperty)

from api.neo_models import SBObject


class Giftlist(SBObject):
    """
    Giftlists are lists of Products which users can purchase for a Mission.
    They are list of items available on Amazon and found via the
    Amazon Product API.

    Initially a Mission will only be able to have one Giftlist and they will
    be able to add or remove items from it via the management area of settings.
    In the future Missions will be able to have multiple Giftlists and set up
    events to require a certain number of gifts or money to be
    provided to run the event.
    """
    # Whether or not the list is currently able to be viewed by the public or
    # if it is still being edited
    public = BooleanProperty(default=False)

    # Which Mission has this list of gifts they want from their supporters
    mission = RelationshipTo("sb_missions.neo_models.Mission", "LIST_FOR")


class Product(SBObject):
    """
    Products are items which are found via the Amazon Product API and
    are used to represent an item available on Amazon in a
    Giftlist owned by Missions.
    """
    # Can use ItemLookup from Amazon to get more information such as price,
    # availability, etc. using the amazon_id
    amazon_id = StringProperty()

    # Whether or not this item has been purchased for the Mission
    purchased = BooleanProperty(default=False)

    # relationships
    # Which list this product is in
    giftlist = RelationshipTo("sb_gifts.neo_models.Giftlist", "IN_LIST")
