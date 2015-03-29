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
        try:
            return reverse("profile_page",
                           kwargs={"pleb_username":
                                self.posted_on_wall.all()[
                                    0].owner.all()[0].username})
        except IndexError:
            return False

    def create_notification(self, pleb, sb_object=None):
        return {
            "action": self.action,
            "url": self.get_url(),
            "from": {
                "profile_pic": pleb.profile_pic,
                "full_name": pleb.get_full_name(),
                "username": pleb.username
            }
        }

    @apply_defense
    def get_single_dict(self):
        from sb_comments.neo_models import SBComment
        try:
            comment_array = []
            query = 'MATCH (p:SBPost) WHERE p.object_uuid="%s" ' \
                    'WITH p MATCH (p) - [:HAS_A] - (c:SBComment) ' \
                    'WHERE c.to_be_deleted=False ' \
                    'WITH c ORDER BY c.created ' \
                    'RETURN c' % self.object_uuid
            post_comments, meta = execute_cypher_query(query)
            post_comments = [SBComment.inflate(row[0]) for row in post_comments]
            try:
                post_owner = self.owned_by.all()[0]
            except IndexError as e:
                return e

            self.view_count += 1
            self.save()
            for comment in post_comments:
                comment_array.append(comment.get_single_dict())
            try:
                parent_object = self.posted_on_wall.all()[
                                    0].owner.all()[0].username
            except(CypherException, IOError, IndexError) as e:
                return e
            return {
                'content': self.content, 'object_uuid': self.object_uuid,
                'vote_count': self.get_vote_count(),
                'upvotes': self.get_upvote_count(),
                'downvotes': self.get_downvote_count(),
                'last_edited_on': unicode(self.last_edited_on),
                'post_owner_full_name': "%s %s" % (post_owner.first_name,
                                                   post_owner.last_name),
                'post_owner_username': post_owner.username,
                "profile_pic": post_owner.profile_pic,
                'comments': comment_array,
                'created': unicode(self.created),
                # Username of the owner of the wall the object is post on
                'parent_object': parent_object,
                'object_type': self.object_type,
            }
        except CypherException as e:
            return e

    @apply_defense
    def render_post_wall_html(self, user):
        try:
            try:
                owner = self.owned_by.all()[0]
            except IndexError as e:
                return e
            post_dict = self.get_single_dict(owner)
            post_dict["user"] = {"username": user.username}
            return render_to_string('post.html', post_dict)

        except(CypherException, IOError) as e:
            return e
