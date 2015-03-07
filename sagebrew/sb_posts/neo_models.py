from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from neomodel import (RelationshipTo, CypherException)

from api.utils import execute_cypher_query
from sb_base.neo_models import SBNonVersioned
from sb_base.decorators import apply_defense



class SBPost(SBNonVersioned):
    sb_name = "post"
    table = 'posts'
    action = "posted on your wall"
    object_type = "01bb301a-644f-11e4-9ad9-080027242395"
    # relationships
    posted_on_wall = RelationshipTo('sb_wall.neo_models.SBWall', 'POSTED_ON')
    #TODO Implement referenced_by_... relationships
    #TODO Implement ..._referenced relationships

    @apply_defense
    def create_relations(self, pleb, question=None, wall=None):
        if wall is None:
            return False
        try:
            self.posted_on_wall.connect(wall)
            wall.post.connect(self)
            rel = self.owned_by.connect(pleb)
            rel.save()
            rel_from_pleb = pleb.posts.connect(self)
            rel_from_pleb.save()
            return True
        except CypherException as e:
            return e

    def get_url(self):
        return reverse("profile_page",
                       kwargs={"pleb_username":
                            self.posted_on_wall.all()[
                                0].owner.all()[0].username})

    def create_notification(self, pleb, sb_object=None):
        return {
            "profile_pic": pleb.profile_pic,
            "full_name": pleb.get_full_name(),
            "action": self.action,
            "url": self.get_url()
        }

    @apply_defense
    def get_single_dict(self, pleb=None):
        from sb_comments.neo_models import SBComment
        try:
            comment_array = []
            query = 'MATCH (p:SBPost) WHERE p.sb_id="%s" ' \
                    'WITH p MATCH (p) - [:HAS_A] - (c:SBComment) ' \
                    'WHERE c.to_be_deleted=False ' \
                    'WITH c ORDER BY c.created_on ' \
                    'RETURN c' % self.sb_id
            post_comments, meta = execute_cypher_query(query)
            post_comments = [SBComment.inflate(row[0]) for row in post_comments]
            post_owner = self.owned_by.all()[0]
            self.view_count += 1
            self.save()
            for comment in post_comments:
                comment_array.append(comment.get_single_dict(pleb))
            return {'content': self.content, 'object_uuid': self.sb_id,
                    'parent_object': self.posted_on_wall.all()[0].
                        owner.all()[0].username,
                    'vote_count': self.get_vote_count(),
                    'up_vote_number': self.get_upvote_count(),
                    'down_vote_number': self.get_downvote_count(),
                    'last_edited_on': unicode(self.last_edited_on),
                    'post_owner': post_owner.first_name + ' ' +
                                  post_owner.last_name,
                    'post_owner_email': post_owner.email,
                    'comments': comment_array,
                    'current_user': pleb,
                    'datetime': unicode(self.date_created),
                    'object_type': self.object_type,
                    'view_count': self.get_view_count()}
        except CypherException as e:
            return e

    @apply_defense
    def render_post_wall_html(self, pleb):
        try:
            return render_to_string('post.html',
                                    self.get_single_dict(pleb))
        except CypherException as e:
            return e
