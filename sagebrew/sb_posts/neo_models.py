from rest_framework.reverse import reverse

from neomodel import (RelationshipTo, StringProperty, db)

from sb_base.neo_models import SBPrivateContent
from plebs.neo_models import Pleb


class Post(SBPrivateContent):
    table = StringProperty(default='posts')
    action_name = StringProperty(default="posted on your wall")

    # optimizations
    wall_owner_username = StringProperty()

    # relationships
    posted_on_wall = RelationshipTo('sb_wall.neo_models.Wall', 'POSTED_ON')

    def get_url(self, request=None):
        return reverse('profile_page', kwargs={
            'pleb_username': self.get_wall_owner_profile().username
        }, request=request)

    def get_wall_owner_profile(self):
        return Pleb.get(self.wall_owner_username)
