from json import loads
from django.conf import settings

from bomberman.client import Client

def get_post_data(request):
    '''
    used when dealing with data from an ajax call or from a regular post.
    determines whether to get the data from request.DATA or request.body

    :param request:
    :return:
    '''
    post_info = request.DATA
    if not post_info:
        try:
            post_info = loads(request.body)
        except ValueError:
            return {}
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