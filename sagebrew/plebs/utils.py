from socket import error as SocketError
from django.template.loader import render_to_string
from neomodel import DoesNotExist, CypherException
from .neo_models import Pleb


def prepare_user_search_html(pleb=""):
    '''
    This utils returns a rendered to string html object used for when a user
    appears in search results

    :param pleb:
    :return:
    '''
    try:
        pleb = Pleb.nodes.get(email=pleb)
    except(Pleb.DoesNotExist, DoesNotExist):
        return False
    except(CypherException, SocketError):
        return None
    pleb_data = {
        'full_name': pleb.first_name + ' ' + pleb.last_name,
        'reputation': 0, 'username': pleb.username,
        'mutual_friends': 0
    }
    html = render_to_string('sb_search_section/pleb_search.html', pleb_data)
    return html

