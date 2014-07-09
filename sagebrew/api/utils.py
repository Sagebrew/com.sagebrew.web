from json import loads
from django.conf import settings

from bomberman.client import Client

def get_post_data(request):
    post_info = request.DATA
    if not post_info:
        post_info = loads(request.body)
    return post_info


def language_filter(content):
    bomberman = Client()
    if bomberman.is_profane(content) ==True:
        corrected_content = bomberman.censor(content)
        return corrected_content
    else:
        return content