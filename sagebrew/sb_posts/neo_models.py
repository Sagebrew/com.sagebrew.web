import pytz
import logging
from json import dumps
from uuid import uuid1
from datetime import datetime
from django.template.loader import render_to_string

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, CypherException)

from api.utils import execute_cypher_query
from sb_base.neo_models import SBNonVersioned

logger = logging.getLogger("loggly_logs")




class SBPost(SBNonVersioned):
    allowed_flags = ["explicit", "spam","other"]
    sb_name = "post"

    # relationships
    posted_on_wall = RelationshipTo('sb_wall.neo_models.SBWall', 'POSTED_ON')
    #TODO Implement referenced_by_... relationships
    #TODO Implement ..._referenced relationships

    def create_relations(self, pleb, question=None, wall=None):
        try:
            self.posted_on_wall.connect(wall)
            wall.post.connect(self)
            rel = self.owned_by.connect(pleb)
            rel.save()
            rel_from_pleb = pleb.posts.connect(self)
            rel_from_pleb.save()
        except Exception as e:
            logger.exception(dumps({"function":
                                        SBPost.create_relations.__name__,
                                    "exception": "Unhandled Exception"}))
            return e

    def get_post_dictionary(self, pleb):
        from sb_comments.neo_models import SBComment
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
            comment_array.append(comment.get_comment_dict(pleb))
        post_dict = {'content': self.content, 'sb_id': self.sb_id,
                     'vote_count': self.get_vote_count(),
                     'up_vote_number': self.get_upvote_count(),
                     'down_vote_number': self.get_downvote_count(),
                     'last_edited_on': str(self.last_edited_on),
                     'post_owner': post_owner.first_name + ' ' +
                                   post_owner.last_name,
                     'post_owner_email': post_owner.email,
                     'comments': comment_array,
                     'current_user': pleb}
        return post_dict

    def render_post_wall_html(self, pleb):
        return render_to_string('sb_post.html', self.get_post_dictionary(pleb))
