from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .utils import prepare_user_search_html
from api.utils import post_to_api
from plebs.neo_models import Pleb
from sb_registration.utils import (get_friends, generate_profile_pic_url)


@login_required()
def profile_page(request, pleb_email):
    '''
    Displays the users profile_page. This is where we call the functions to
    determine
    who the senators are for the plebs state and which representative for
    the plebs
    district. Checks to see if the user currently accessing the page is the
    same user
    as the one who owns the page. if so it loads the page fully, if the user
    is a firend
    of the owner of the page then it allows them to see posts and comments
    on posts on the
    owners wall. If the user is neither the owner nor a friend then it only
    shows the users
    name, congressmen, reputation and profile pictures along with a button
    that allows
    them to send a friend request.

    :param request:
    :return:
    '''
    citizen = Pleb.index.get(email=pleb_email)
    current_user = request.user
    page_user = User.objects.get(email=pleb_email)
    is_owner = False
    is_friend = False
    friends_list = get_friends(citizen.email)
    if current_user.email == page_user.email:
        is_owner = True
    elif citizen.traverse('friends').where('email', '=',
                                           current_user.email).run():
        is_friend = True
    # TODO check for index error
    # TODO check why address does not always work
    # TODO deal with address and senator/rep in a util + task
    # address = citizen.traverse('address').run()[0]
    #sen_array = determine_senators(address)
    #rep_array = determine_reps(address)
    post_data = {'email': citizen.email, 'range_end': 5,
                 'range_start': 0}
    headers = {'content-type': 'application/json'}
    user_posts = post_to_api(reverse('get_user_posts'), post_data, headers)
    notification_data = {'email': citizen.email, 'range_end': 5,
                         'range_start': 0}
    notifications = post_to_api(reverse('get_notifications'),
                                notification_data, headers=headers)
    citizen.profile_pic = generate_profile_pic_url(citizen.profile_pic_uuid)
    citizen.save()
    return render(request, 'profile_page.html', {
        'pleb_info': citizen,
        'current_user': current_user.email,
        'page_user': page_user.email,
        #'senator_names': sen_array,
        #'rep_name': rep_array,
        'user_posts': user_posts,
        'notifications': notifications,
        'is_owner': is_owner,
        'is_friend': is_friend,
        'friends_list': friends_list,
    })

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_user_search_view(request, pleb_email=""):
    '''
    This view will take a plebs email, get the user and render to string
    an html object which holds the data to be displayed when a user is returned
    in a search.

    :param request:
    :param pleb:
    :return:
    '''
    try:
        response = prepare_user_search_html(pleb_email)
        return Response({'html': response}, status=200)
    except:
        return Response({'html': []}, status=400)

