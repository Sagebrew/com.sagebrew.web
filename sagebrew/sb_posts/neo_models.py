from rest_framework.reverse import reverse

from neomodel import (RelationshipTo, StringProperty)

from sb_base.neo_models import SBPrivateContent


class Post(SBPrivateContent):
    table = StringProperty(default='posts')
    action_name = StringProperty(default="posted on your wall")

    # relationships
    posted_on_wall = RelationshipTo('sb_wall.neo_models.Wall', 'POSTED_ON')

    def get_url(self, request=None):
        wall_owner = self.posted_on_wall.all()[0].get_owned_by()
        return reverse('profile_page', kwargs={
            'pleb_username': wall_owner.username
        }, request=request)
