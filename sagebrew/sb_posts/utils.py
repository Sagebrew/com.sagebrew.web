import pytz
import logging
from uuid import uuid1
from json import dumps
from datetime import datetime

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


def edit_post_info(post_uuid, content, last_edited_on):
    '''
    changes the content of the post linked to the id passed to the function
    to the content which was passed

    :param content: "test post",
    :param post_uuid: str(uuid)[:36]
    :param last_edited_on: datetime.now(pytz.utc)
    :return:
            if the post's value to_be_deleted is True it returns the detail
            to be deleted

            if the content of the edit is the same as the content already in
            the post it returns the detail content is the same

            if the timestamp of the edit is the same it returns the
            detail last edit more recent

            if it is successful in editing it returns True
    '''
    try:
        try:
            my_post = SBPost.nodes.get(sb_id=post_uuid)
        except (SBPost.DoesNotExist) as e:
            # TODO should we fail out here rather than retry?
            # I think we should keep retrying since if we have gotten to
            # edit the post must have been displayed to the user
            # meaning it had been spawned for creation at some point
            # and deletion only means the content will be whiped and it
            # will be taken down from view.
            return e
        if my_post.to_be_deleted:
            return False
        if my_post.content == content:
            return False
        if my_post.last_edited_on >= last_edited_on:
            return False

        my_post.content = content
        my_post.last_edited_on = last_edited_on
        if my_post.edited is False:
            my_post.edited = True

        my_post.save()
        return True
    except DoesNotExist:
        return ValueError("SBPost does not exist")
    except Exception as e:
        logger.exception(dumps({"function": edit_post_info.__name__,
                                "exception": "Unhandled Exception"}))
        return e


def delete_post_info(sb_id):
    '''
    Removes the personal content of the post and all comments attached to it

    :param sb_id = String representing a UUID
    :return:
            if the post and comments are successfully deleted it returns True

            if it cant find the post it returns False
    '''
    try:
        try:
            my_post = SBPost.nodes.get(sb_id=sb_id)
        except (SBPost.DoesNotExist):
            return False

        if datetime.now(pytz.utc).day - my_post.delete_time.day >= 1:
            post_comments = my_post.comments.all()
            for comment in post_comments:
                comment.content = ""
                comment.save()
            my_post.content = ""
            my_post.save()
            return True
        else:
            return True
    except Exception as e:
        logger.exception(dumps({'function': delete_post_info.__name__,
                                "exception": "Unhandled Exception"}))
        return e
