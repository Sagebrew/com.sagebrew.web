from neomodel import (RelationshipTo)

from sb_base.neo_models import SBPrivateContent


class Post(SBPrivateContent):
    table = 'posts'
    action_name = "posted on your wall"
    object_type = "01bb301a-644f-11e4-9ad9-080027242395"

    # relationships
    posted_on_wall = RelationshipTo('sb_wall.neo_models.Wall', 'POSTED_ON')