from django.dispatch import Signal

friend_request_sent = Signal(providing_args=["user", "friend"])
friend_request_accepted = Signal(providing_args=[
                                                 'user', 'friend', 'permission'
                                                ])
friend_removed = Signal(providing_args=['user', 'friend', 'permission'])
