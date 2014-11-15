import logging
from uuid import uuid1
from json import dumps

from neomodel import DoesNotExist

from api.utils import execute_cypher_query, spawn_task
from sb_base.tasks import create_object_relations_task
from plebs.neo_models import Pleb
from .neo_models import SBPost

logger = logging.getLogger('loggly_logs')


def get_pleb_posts(pleb_object, range_end, range_start='0'):
    '''
    Gets all the posts which are attached to the page users wall aswell as the
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
                     % (pleb_object.email, range_start, str(range_end))
        pleb_posts, meta = execute_cypher_query(post_query)
        posts = [SBPost.inflate(row[0]) for row in pleb_posts]
        return posts
    except IndexError as e:
        return e
    except Exception as e:
        logger.exception(dumps({"function": get_pleb_posts.__name__,
                                "exception": "Unhandled Exception"}))
        return e


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
        relation_data = {'sb_object': my_post,
                         'current_pleb': current_pleb,
                         'wall': my_citizen.wall.all()[0]}
        spawn_task(task_func=create_object_relations_task,
                       task_param=relation_data)
        return my_post
    except (ValueError, IndexError) as e:
        return e
    except Exception as e:
        logger.exception(dumps({"function": save_post.__name__,
                                "exception": "Unhandled Exception"}))
        return e

