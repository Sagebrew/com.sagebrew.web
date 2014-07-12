import os
import hashlib
from json import dumps

from django.conf import settings
from uuid import uuid1
from requests import post as request_post
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth.models import User

from plebs.neo_models import Pleb, TopicCategory, SBTopic, Address

from sb_registration.utils import (determine_senators, determine_reps, get_friends)



@login_required()
def profile_page(request, pleb_email):
    '''
    Displays the users profile_page. This is where we call the functions to determine
    who the senators are for the plebs state and which representative for the plebs
    district. Checks to see if the user currently accessing the page is the same user
    as the one who owns the page. if so it loads the page fully, if the user is a firend
    of the owner of the page then it allows them to see posts and comments on posts on the
    owners wall. If the user is neither the owner nor a friend then it only shows the users
    name, congressmen, reputation and profile pictures along with a button that allows
    them to send a friend request.

    :param request:
    :return:
    '''
    citizen = Pleb.index.get(email=pleb_email)
    current_user = request.user
    page_user = User.objects.get(email = pleb_email)
    is_owner = False
    is_friend = False
    friends_list = get_friends(citizen.email)
    print friends_list
    if current_user.email == page_user.email:
        is_owner = True
    elif citizen.traverse('friends').where('email','=',current_user.email).run():
        is_friend = True

    print "is owner", is_owner
    print "is friend", is_friend
    # TODO check for index error
    # TODO check why address does not always work
    # TODO deal with address and senator/rep in a util + task
    #address = citizen.traverse('address').run()[0]
    #sen_array = determine_senators(address)
    #rep_array = determine_reps(address)
    post_data = {'email': citizen.email}
    headers = {'content-type': 'application/json'}
    post_req = request_post('https://192.168.56.101/posts/query_posts/',
                            data=dumps(post_data), verify=False, headers=headers)
    user_posts = post_req.json()
    '''
    notification_req = request_post('https://192.168.56.101/notifications/query_notifications/',
                                    data=dumps(post_data), verify=False, headers=headers)
    user_notifications = notification_req.json()
    '''
    '''
    friend_requests_req = request_post('https://192.168.56.101/notifications/query_friend_requests/',
                                       data=dumps(post_data), verify=False, headers=headers)
    user_friend_requests = friend_requests_req.json()
    '''

    return render(request, 'profile_page.html', {
                                                 'pleb_info': citizen,
                                                 'current_user': current_user.email,
                                                 'page_user': page_user.email,
                                                 #'senator_names': sen_array,
                                                 #'rep_name': rep_array,
                                                 'user_posts': user_posts,
                                                 #'user_notifications': user_notifications,
                                                 #'user_friend_requests': user_friend_requests,
                                                 'is_owner': is_owner,
                                                 'is_friend': is_friend,
                                                 'friends_list': friends_list,
                                                 })

