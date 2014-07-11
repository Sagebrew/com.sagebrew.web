from plebs.neo_models import Pleb
from .neo_models import FriendRequest


def create_friend_request_util(data):
    '''
    If the function cant find either the to or from pleb it ends, if
    it does find them then it will create a friend request and
    create the relationships from the users to the friend requests
    '''
    try:
        from_citizen = Pleb.index.get(email = data['from_pleb'])
        to_citizen = Pleb.index.get(email = data['to_pleb'])
    except Pleb.DoesNotExist:
        return False

    requests = from_citizen.traverse('friend_requests_sent').run()
    for request in requests:
        if request.traverse('request_to').where('email','=',to_citizen.email).run():
            print 'found matching request'
            return True

    data.pop('from_pleb', None)
    data.pop('to_pleb', None)
    friend_request = FriendRequest(**data)
    friend_request.save()
    friend_request.request_from.connect(from_citizen)
    friend_request.request_to.connect(to_citizen)
    friend_request.save()
    from_citizen.friend_requests_sent.connect(friend_request)
    from_citizen.save()
    to_citizen.friend_requests_recieved.connect(friend_request)
    to_citizen.save()
    print 'request successfully sent'
