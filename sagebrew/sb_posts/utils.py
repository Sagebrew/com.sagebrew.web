from uuid import uuid1

from api.utils import spawn_task
from plebs.neo_models import Pleb
from sb_comments.utils import get_post_comments
from .neo_models import SBPost


def get_pleb_posts(pleb_object, range_end, range_start):
    '''
    Gets all the posts which are attached to the page users wall aswell as the
    comments associated with the posts

    :param pleb_object:
                        This is an instance of a Pleb object
    :return:
    '''
    try:
        pleb_wall = pleb_object.traverse('wall').run()[0]
        pleb_posts = pleb_wall.traverse('post').where('to_be_deleted', '=',
            False).order_by_desc('date_created').skip(range_start).limit(
            range_end).run()
        return get_post_comments(pleb_posts)
    except:
        print "failed to retrieve posts"
        return {"details": "You have no posts!"}


def save_post(post_uuid=str(uuid1()), content="", current_pleb="",
              wall_pleb=""):
    '''
    saves a post and creates the relationships between the wall
    and the poster of the comment


    :param post_info:
                    post_info = {
                        'content': "this is a post",
                        'current_pleb': "tyler.wiersing@gmail.com",
                        'wall_pleb': "devon@sagebrew.com",
                        'post_uuid': str(uuid1())
                    }
    :return:
            if post exists returns None
            else returns SBPost object
    '''
    try:
        test_post = SBPost.index.get(post_id=post_uuid)
    except SBPost.DoesNotExist:
        poster = Pleb.index.get(email=current_pleb)
        my_citizen = Pleb.index.get(email=wall_pleb)
        my_post = SBPost(content=content, post_id=post_uuid)
        my_post.save()
        wall = my_citizen.traverse('wall').run()[0]
        my_post.posted_on_wall.connect(wall)
        wall.post.connect(my_post)
        rel = my_post.owned_by.connect(poster)
        rel.save()
        rel_from_pleb = poster.posts.connect(my_post)
        rel_from_pleb.save()
        return my_post
    except ValueError:
        return None
    except:
        return None


def edit_post_info(content="", post_uuid=str(uuid1()), last_edited_on=None,
                   current_pleb=None):
    '''
    changes the content of the post linked to the id passed to the function
    to the content which was passed

    :param post_info:
                post_info{
                    content: "test post",
                    post_uuid: str(uuid)[:36],
                    last_edited_on: datetime.now(pytz.utc),
                    current_pleb: 'fake_email@gmail.com',
                }
    :return:
            if the post's value to_be_deleted is True it returns the detail
            to be deleted

            if the content of the edit is the same as the content already in
            the post it returns the detail content is the same

            if the timestamp of the edit is the same it returns the
            detail last edit more recent

            if it is successful in editing it returns True
    '''
    # TODO create a function to determine if the object will be edited
    try:
        my_post = SBPost.index.get(post_id=post_uuid)
        if my_post.to_be_deleted:
            return {'post': my_post, 'detail': 'to be deleted'}

        if my_post.content == content:
            return {'post': my_post, 'detail': 'content is the same'}

        if my_post.last_edited_on == last_edited_on:
            return {
                'post': my_post,
                'detail': 'time stamp is the same'
            }
        try:
            if my_post.last_edited_on > last_edited_on:
                return {'post': my_post, 'detail': 'last edit more recent'}
        except TypeError:
            pass

        my_post.content = content
        my_post.last_edited_on = last_edited_on
        my_post.save()
        return True
    except SBPost.DoesNotExist:
        return {'detail': 'post does not exist yet'}


def delete_post_info(post_id=str(uuid1())):
    '''
    deletes the post and all comments attached to it

    :param post_info:
                    post_uuid = str(uuid1)
    :return:
            if the post and comments are successfully deleted it returns True

            if it cant find the post it returns False
    '''
    try:
        my_post = SBPost.index.get(post_id=post_id)
        post_comments = my_post.traverse('comments')
        for comment in post_comments:
            comment.delete()
        my_post.delete()
        return True
    except SBPost.DoesNotExist:
        return False


def create_post_vote(pleb="", post_uuid=str(uuid1()), vote_type=""):
    '''
    determines if the user has voted on this post yet, if not then it allows
    the vote and creates it, if not it does not allow.

    :param post_info:
                    pleb = "tyler.wiersing@gmail.com"
                    post_uuid = str(uuid1())
                    vote_type = "" up/down
    :return:

    '''
    # TODO This needs to allow to changing of vote
    from sb_posts.tasks import create_downvote_post, create_upvote_post

    my_pleb = Pleb.index.get(email=pleb)
    my_post = SBPost.index.get(post_id=post_uuid)
    if my_post.up_voted_by.is_connected(
            my_pleb) or my_post.down_voted_by.is_connected(my_pleb):
        return False
    else:
        if vote_type == 'up':
            task_param = {'post_uuid': post_uuid,
                          'pleb': pleb}
            spawn_task(task_func=create_upvote_post, task_param=task_param)
            return True
        elif vote_type == 'down':
            task_param = {'post_uuid': post_uuid,
                          'pleb': pleb}
            spawn_task(task_func=create_downvote_post, task_param=task_param)
            return True

