import logging

from neomodel.exception import CypherException, DoesNotExist

from api.utils import execute_cypher_query
from .neo_models import SBPost
from sb_base.decorators import apply_defense

logger = logging.getLogger('loggly_logs')


@apply_defense
def get_pleb_posts(pleb_object, range_end, range_start=0):
    '''
    Gets all the posts which are attached to the page users wall as well as the
    comments associated with the posts

    :param pleb_object:
                        This is an instance of a Pleb object
    :return:
    '''
    try:
        post_query = 'MATCH (pleb:Pleb) WHERE pleb.email="%s" ' \
                     'WITH pleb ' \
                     'MATCH (pleb)-[:OWNS_WALL]-(wall) ' \
                     'WITH wall ' \
                     'MATCH (wall)-[:HAS_POST]-(posts:SBPost) ' \
                     'WHERE posts.to_be_deleted=False ' \
                     'WITH posts ' \
                     'ORDER BY posts.date_created DESC ' \
                     'SKIP %s LIMIT %s ' \
                     'RETURN posts'\
                     % (pleb_object.email, str(range_start), str(range_end))
        pleb_posts, meta = execute_cypher_query(post_query)
        posts = [SBPost.inflate(row[0]) for row in pleb_posts]
        return posts
    except IndexError as e:
        return e


@apply_defense
def save_post(content, post_uuid):
    '''
    saves a post and creates the relationships between the wall
    and the poster of the comment


    :param content: "this is a post",
    :param current_pleb: "tyler.wiersing@gmail.com",
    :param wall_pleb: "devon@sagebrew.com",
    :param post_uuid: str(uuid1())
    :return:
            if post exists returns None
            else returns SBPost object
    '''
    try:
        sb_post = SBPost.nodes.get(sb_id=post_uuid)
    except(SBPost.DoesNotExist, DoesNotExist):
        try:
            sb_post = SBPost(content=content, sb_id=post_uuid)
            sb_post.save()
        except CypherException as e:
            return e
    except CypherException as e:
        return e
    return sb_post