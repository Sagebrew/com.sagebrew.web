from django.template.loader import render_to_string
from django.core.cache import cache

from neomodel import DoesNotExist, CypherException

from sb_base.decorators import apply_defense
from api.utils import execute_cypher_query

from .neo_models import Pleb, FriendRequest


def prepare_user_search_html(pleb):
    '''
    This utils returns a rendered to string html object used for when a user
    appears in search results

    :param pleb:
    :return:
    '''
    profile = cache.get(pleb)
    if profile is None:
        try:
            profile = Pleb.nodes.get(username=pleb)
        except(Pleb.DoesNotExist, DoesNotExist):
            return False
        except(CypherException, IOError):
            return None
        cache.set(pleb, profile)

    pleb_data = {
        'full_name': profile.first_name + ' ' + profile.last_name,
        'reputation': 0, 'username': profile.username,
    }
    html = render_to_string('user_search_block.html', pleb_data)
    return html


@apply_defense
def create_friend_request_util(from_username, to_username, object_uuid):
    """
    If the function cant find either the to or from pleb it ends, if
    it does find them then it will create a friend request and
    create the relationships from the users to the friend requests
    """
    try:
        try:
            from_citizen = Pleb.nodes.get(username=from_username)
            to_citizen = Pleb.nodes.get(username=to_username)
        except(Pleb.DoesNotExist, DoesNotExist) as e:
            return e
        except(CypherException, IOError) as e:
            return e

        query = 'match (p:Pleb) where p.username="%s" ' \
                'with p ' \
                'match (p)-[:SENT_A_REQUEST]-(r:FriendRequest) ' \
                'with p, r ' \
                'match (r)-[:REQUEST_TO]-(p2:Pleb) where p2.username="%s" ' \
                'return p2' % (from_username, to_username)
        pleb2, meta = execute_cypher_query(query)
        if isinstance(pleb2, Exception):
            return pleb2
        if pleb2:
            return True

        friend_request = FriendRequest(object_uuid=object_uuid)
        friend_request.save()
        friend_request.request_from.connect(from_citizen)
        friend_request.request_to.connect(to_citizen)
        friend_request.save()
        from_citizen.friend_requests_sent.connect(friend_request)
        from_citizen.save()
        to_citizen.friend_requests_received.connect(friend_request)
        to_citizen.save()
        return True
    except(CypherException, KeyError) as e:
        return e


def get_filter_by(filter_by):
    if filter_by == "":
        return ""
    if filter_by == "sent":
        return "[:SENT_A_REQUEST]"
    if filter_by == "received":
        return "[:RECEIVED_A_REQUEST]"
