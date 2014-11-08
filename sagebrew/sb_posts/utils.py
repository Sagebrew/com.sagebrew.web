import logging
from uuid import uuid1
from json import dumps

from neomodel import DoesNotExist

from api.utils import execute_cypher_query
from plebs.neo_models import Pleb
from sb_comments.utils import get_post_comments
from .neo_models import SBPost

logger = logging.getLogger('loggly_logs')


def get_pleb_posts(pleb_object, range_end, range_start):
    '''
    Gets all the posts which are attached to the page users wall aswell as the
    comments associated with the posts

    :param pleb_object:
                        This is an instance of a Pleb object
    :return:
    '''
    try:
        # TODO is range start needed anymore? Should it go where str(0) is?
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
                     % (pleb_object.email, str(0), str(range_end))
        pleb_posts, meta = execute_cypher_query(post_query)
        posts = [SBPost.inflate(row[0]) for row in pleb_posts]
        return get_post_comments(posts)
    except IndexError:
        return {'details': 'something broke'}
    except Exception:
        logger.exception(dumps({"function": get_pleb_posts.__name__,
                                "exception": "Unhandled Exception"}))
        return {"details": "You have no posts!"}


def save_post(current_pleb, wall_pleb, content, post_uuid=None):
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
    if post_uuid is None:
        post_uuid = str(uuid1())
    try:
        SBPost.nodes.get(sb_id=post_uuid)
        return True
    except SBPost.DoesNotExist:
        try:
            poster = Pleb.nodes.get(email=current_pleb)
            my_citizen = Pleb.nodes.get(email=wall_pleb)
        except (Pleb.DoesNotExist, DoesNotExist) as e:
            return e
        my_post = SBPost(content=content, sb_id=post_uuid)
        my_post.save()
        wall = my_citizen.wall.all()[0]
        my_post.posted_on_wall.connect(wall)
        wall.post.connect(my_post)
        rel = my_post.owned_by.connect(poster)
        rel.save()
        rel_from_pleb = poster.posts.connect(my_post)
        rel_from_pleb.save()
        return my_post
    except ValueError as e:
        return e
    except IndexError as e:
        return e
    except Exception as e:
        logger.exception(dumps({"function": save_post.__name__,
                                "exception": "Unhandled Exception"}))
        return e

