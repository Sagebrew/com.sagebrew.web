import pytz
import logging
from json import dumps
from uuid import uuid1
from datetime import datetime

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException)

from sb_base.neo_models import SBNonVersioned

logger = logging.getLogger("loggly_logs")




class SBPost(SBNonVersioned):
    allowed_flags = ["explicit", "spam","other"]
    sb_name = "post"

    # relationships
    posted_on_wall = RelationshipTo('sb_wall.neo_models.SBWall', 'POSTED_ON')
    #TODO Implement referenced_by_... relationships
    #TODO Implement ..._referenced relationships



