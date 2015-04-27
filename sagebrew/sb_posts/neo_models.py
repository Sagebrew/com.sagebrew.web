from rest_framework.reverse import reverse

from neomodel import (RelationshipTo)

from sb_base.neo_models import SBPrivateContent


class Post(SBPrivateContent):
    table = 'posts'
    action_name = "posted on your wall"

    # relationships
    posted_on_wall = RelationshipTo('sb_wall.neo_models.Wall', 'POSTED_ON')

    def get_url(self, request=None):
        owner = self.owned_by.all()[0]
        return reverse('profile_page', kwargs={'pleb_username': owner.username},
                       request=request)