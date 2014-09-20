from django.template.loader import render_to_string
from django.conf import settings

from .neo_models import Pleb

def prepare_user_search_html(pleb=""):
    '''
    This utils returns a rendered to string html object used for when a user
    appears in search results

    :param pleb:
    :return:
    '''
    pleb = Pleb.nodes.get(email=pleb)
    pleb_data = {
        'full_name': pleb.first_name + ' ' + pleb.last_name,
        'reputation': 0, 'pleb_url': settings.WEB_ADDRESS+'/user/'+pleb.email,
        'mutual_friends': 0
    }
    html = render_to_string('pleb_search.html', pleb_data)
    return html