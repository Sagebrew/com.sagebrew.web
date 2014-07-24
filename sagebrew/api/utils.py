from json import loads
from django.conf import settings

from bomberman.client import Client

from sb_comments.neo_models import SBComment
from sb_posts.neo_models import SBPost, SBAnswer, SBQuestion
from sb_garbage.neo_models import SBGarbageCan

def get_post_data(request):
    '''
    used when dealing with data from an ajax call or from a regular post.
    determines whether to get the data from request.DATA or request.body

    :param request:
    :return:
    '''
    post_info = request.DATA
    if not post_info:
        post_info = loads(request.body)
    return post_info


def language_filter(content):
    '''
    Filters harsh language from posts and commments using the bomberman client which
    is initialized each time the function is called.

    :param content:
    :return:
    '''
    bomberman = Client()
    if bomberman.is_profane(content) ==True:
        corrected_content = bomberman.censor(content)
        return corrected_content
    else:
        return content

def post_to_garbage(post_id):
    try:
        post = SBPost.index.get(post_id=post_id)
        garbage_can = SBGarbageCan.index.get(garbage_can='garbage')
        post.to_be_deleted = True
        garbage_can.posts.connect(post)
        garbage_can.save()
        post.save()
    except SBGarbageCan.DoesNotExist:
        post = SBPost.index.get(post_id=post_id)
        garbage_can = SBGarbageCan(garbage_can='garbage')
        garbage_can.save()
        post.to_be_deleted = True
        garbage_can.posts.connect(post)
        garbage_can.save()
        post.save()
    except SBPost.DoesNotExist:
        pass

def comment_to_garbage(comment_id):
    try:
        comment = SBComment.index.get(comment_id=comment_id)
        garbage_can = SBGarbageCan.index.get(garbage_can='garbage')
        comment.to_be_deleted = False
        garbage_can.comments.connect(comment)
        garbage_can.save()
        comment.save()
    except SBGarbageCan.DoesNotExist:
        comment = SBComment.index.get(comment_id=comment_id)
        garbage_can = SBGarbageCan(garbage_can='garbage')
        garbage_can.save()
        comment.to_be_deleted = False
        garbage_can.comments.connect(comment)
        garbage_can.save()
        comment.save()
    except SBComment.DoesNotExist:
        pass