from json import loads

from django.conf import settings

from bomberman.client import Client

def get_post_data(request):
    try:
        post_info = loads(request.body)
    except(ValueError):
        post_info = request.DATA
    return post_info

def language_filter(content):
    bomberman = Client()
    if bomberman.is_profane(content) ==True:
        corrected_content = bomberman.censor(content)
        return corrected_content
    else:
        return content