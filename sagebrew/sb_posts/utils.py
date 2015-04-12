from neomodel.exception import CypherException, DoesNotExist

from api.utils import execute_cypher_query
from .neo_models import Post
from sb_base.decorators import apply_defense


@apply_defense
def get_page_user_posts(username, range_end, range_start=0):
    '''
    Gets all the posts which are attached to the page users wall as well as the
    comments associated with the posts

    :param pleb_object:
                        This is an instance of a Pleb object
    :return:
    '''
    try:
        post_query = 'MATCH (pleb:Pleb) WHERE pleb.username="%s" ' \
                     'WITH pleb ' \
                     'MATCH (pleb)-[:OWNS_WALL]-(wall) ' \
                     'WITH wall ' \
                     'MATCH (wall)-[:HAS_POST]-(posts:Post) ' \
                     'WHERE posts.to_be_deleted=False ' \
                     'WITH posts ' \
                     'ORDER BY posts.created DESC ' \
                     'SKIP %s LIMIT %s ' \
                     'RETURN posts'\
                     % (username, str(range_start), str(range_end))
        pleb_posts, meta = execute_cypher_query(post_query)
        if isinstance(pleb_posts, Exception):
            return pleb_posts
        posts = [Post.inflate(row[0]) for row in pleb_posts]
        return posts
    except IndexError as e:
        return e


@apply_defense
def save_post(content, post_uuid, created):
    '''
    saves a post and creates the relationships between the wall
    and the poster of the comment


    :param content: "this is a post",
    :param current_pleb: "tyler.wiersing@gmail.com",
    :param wall_pleb: "devon@sagebrew.com",
    :param post_uuid: str(uuid1())
    :return:
            if post exists returns None
            else returns Post object
    '''
    try:
        sb_post = Post.nodes.get(object_uuid=post_uuid)
    except(Post.DoesNotExist, DoesNotExist):
        sb_post = Post(content=content, object_uuid=post_uuid,
                         last_edited_on=created, created=created)
        try:
            sb_post.save()
        except(CypherException, IOError) as e:
            return e
    except(CypherException, IOError) as e:
        return e
    return sb_post