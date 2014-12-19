from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from neomodel import DoesNotExist, CypherException

from plebs.neo_models import Pleb
from sb_registration.utils import (get_friends, generate_profile_pic_url,
                                   verify_completed_registration)
from .utils import prepare_user_search_html


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def profile_page(request, pleb_username=""):
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
    try:
        citizen = Pleb.nodes.get(email=request.user.email)
        page_user_pleb = Pleb.nodes.get(username=pleb_username)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect('404_Error')
    except(CypherException):
        return HttpResponse('Server Error', status=500)
    current_user = request.user
    page_user = User.objects.get(email=page_user_pleb.email)
    is_owner = False
    is_friend = False
    friends_list = get_friends(citizen.email)
    if current_user.email == page_user.email:
        is_owner = True
    elif citizen.friends.search(email=current_user.email):
        is_friend = True

    # TODO deal with address and senator/rep in a util + task
    # TODO Create a cypher query to get addresses to replace traverse
    #address = citizen.traverse('address').run()[0]
    #sen_array = determine_senators(address)
    #rep_array = determine_reps(address)

    citizen.profile_pic = generate_profile_pic_url(citizen.profile_pic_uuid)
    citizen.save()
    return render(request, 'sb_plebs_base/profile_page.html', {
        'pleb_info': citizen,
        'current_user': current_user.email,
        'page_user': page_user.email,
        #'senator_names': sen_array,
        #'rep_name': rep_array,
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
    :param pleb_email:
    :return:
    '''
    response = prepare_user_search_html(pleb_email)
    if response is None:
        return HttpResponse('Server Error', status=500)
    elif response is False:
        return HttpResponse('Bad Email', status=400)
    return Response({'html': response}, status=200)


@login_required()
def about_page(request, pleb_username):
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
    try:
        citizen = Pleb.nodes.get(username=pleb_username)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except CypherException:
        return HttpResponse('Server Error', status=500)
    current_user = request.user
    page_user = User.objects.get(email=citizen.email)
    is_owner = False
    is_friend = False
    friends_list = get_friends(citizen.email)
    if current_user.email == page_user.email:
        is_owner = True
    elif citizen.friends.search(email=current_user.email):
        is_friend = True

    # TODO check for index error
    # TODO deal with address and senator/rep in a util + task
    # TODO Create a cypher query to get addresses to replace traverse
    #address = citizen.traverse('address').run()[0]
    #sen_array = determine_senators(address)
    #rep_array = determine_reps(address)

    citizen.profile_pic = generate_profile_pic_url(citizen.profile_pic_uuid)
    citizen.save()
    return render(request, 'sb_about_section/sb_about.html', {
        'pleb_info': citizen,
        'current_user': current_user.email,
        'page_user': page_user.email,
        #'senator_names': sen_array,
        #'rep_name': rep_array,
        'is_owner': is_owner,
        'is_friend': is_friend,
        'friends_list': friends_list,
    })


@login_required()
def reputation_page(request, pleb_username):
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
    try:
        citizen = Pleb.nodes.get(username=pleb_username)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except CypherException:
        return HttpResponse('Server Error', status=500)
    current_user = request.user
    page_user = User.objects.get(email=citizen.email)
    is_owner = False
    is_friend = False
    friends_list = get_friends(citizen.email)
    if current_user.email == page_user.email:
        is_owner = True
    elif citizen.friends.search(email=current_user.email):
        is_friend = True

    # TODO check for index error
    # TODO deal with address and senator/rep in a util + task
    # TODO Create a cypher query to get addresses to replace traverse
    #address = citizen.traverse('address').run()[0]
    #sen_array = determine_senators(address)
    #rep_array = determine_reps(address)

    citizen.profile_pic = generate_profile_pic_url(citizen.profile_pic_uuid)
    citizen.save()
    return render(request, 'sb_reputation_section/sb_reputation.html', {
        'pleb_info': citizen,
        'current_user': current_user.email,
        'page_user': page_user.email,
        #'senator_names': sen_array,
        #'rep_name': rep_array,
        'is_owner': is_owner,
        'is_friend': is_friend,
        'friends_list': friends_list,
    })

@login_required()
def friends_page(request, pleb_username):
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
    try:
        citizen = Pleb.nodes.get(username=pleb_username)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except CypherException:
        return HttpResponse('Server Error', status=500)
    current_user = request.user
    page_user = User.objects.get(email=citizen.email)
    is_owner = False
    is_friend = False
    friends_list = get_friends(citizen.email)
    if current_user.email == page_user.email:
        is_owner = True
    elif citizen.friends.search(email=current_user.email):
        is_friend = True

    # TODO check for index error
    # TODO deal with address and senator/rep in a util + task
    # TODO Create a cypher query to get addresses to replace traverse
    #address = citizen.traverse('address').run()[0]
    #sen_array = determine_senators(address)
    #rep_array = determine_reps(address)

    citizen.profile_pic = generate_profile_pic_url(citizen.profile_pic_uuid)
    citizen.save()
    return render(request, 'sb_friends_section/sb_friends.html', {
        'pleb_info': citizen,
        'current_user': current_user.email,
        'page_user': page_user.email,
        #'senator_names': sen_array,
        #'rep_name': rep_array,
        'is_owner': is_owner,
        'is_friend': is_friend,
        'friends_list': friends_list,
    })