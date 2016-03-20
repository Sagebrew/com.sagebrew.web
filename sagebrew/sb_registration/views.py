from localflavor.us.us_states import US_STATES

from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import get_template
from django.template import Context

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from neomodel import (CypherException, db, DoesNotExist)

from api.utils import spawn_task
from plebs.tasks import send_email_task, update_address_location
from plebs.neo_models import Pleb, Address

from .forms import (AddressInfoForm, InterestForm,
                    ProfilePictureForm,
                    LoginForm)
from .utils import (verify_completed_registration, verify_verified_email)
from .models import token_gen


def advocacy(request):
    if request.user.is_authenticated() is True:
        return redirect('signup')
    return render(request, 'advocacy.html')


def political_campaign(request):
    if request.user.is_authenticated() is True:
        return redirect('signup')
    try:
        query = 'MATCH (position:Position) RETURN COUNT(position)'
        res, _ = db.cypher_query(query)
        position_count = res.one
        if position_count is None:
            position_count = 7274
    except (CypherException, IOError):
        position_count = 7274
    return render(request, 'political_campaign.html',
                  {"position_count": position_count})


def signup_view(request):
    if request.user.is_authenticated() is True:
        try:
            user_profile = Pleb.get(username=request.user.username,
                                    cache_buster=True)
        except DoesNotExist:
            return redirect('404_Error')
        if user_profile.completed_profile_info is True:
            return redirect('newsfeed')
        elif not user_profile.email_verified:
            return redirect('confirm_view')
        elif not user_profile.completed_profile_info:
            return redirect('profile_info')
    return render(request, 'index.html')


def quest_signup(request):
    return redirect('political')


def login_view(request):
    try:
        if request.user.is_authenticated() is True:
            return redirect('root_profile_page')
    except AttributeError:
        pass
    return render(request, 'login.html')


@login_required()
def resend_email_verification(request):
    try:
        profile = Pleb.get(username=request.user.username, cache_buster=True)
    except DoesNotExist:
        return render(request, 'login.html')
    except (CypherException, IOError):
        return redirect('500_Error')

    template_dict = {
        'full_name': request.user.get_full_name(),
        'verification_url': "%s%s%s" % (settings.EMAIL_VERIFICATION_URL,
                                        token_gen.make_token(
                                            request.user, profile), '/')
    }
    subject, to = "Sagebrew Email Verification", request.user.email
    # text_content = get_template(
    # 'email_templates/email_verification.txt').render(Context(template_dict))
    html_content = get_template(
        'email_templates/email_verification.html').render(
        Context(template_dict))
    task_data = {'to': to, 'subject': subject, 'html_content': html_content,
                 "source": "support@sagebrew.com"}
    spawned = spawn_task(task_func=send_email_task, task_param=task_data)
    if isinstance(spawned, Exception):
        return redirect('500_Error')
    return redirect("confirm_view")


@api_view(['POST'])
def login_view_api(request):
    try:
        login_form = LoginForm(request.data)
        valid_form = login_form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form is True:
        try:
            user = User.objects.get(email=login_form.cleaned_data['email'])
        except User.DoesNotExist:
            return Response({'detail': 'Incorrect password and '
                                       'username combination.'},
                            status=400)
        except MultipleObjectsReturned:
            return Response({'detail': 'Appears we have two users with '
                                       'that email. Please contact '
                                       'support@sagebrew.com.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user = authenticate(username=user.username,
                            password=login_form.cleaned_data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                rev = reverse('newsfeed')
                return Response({'detail': 'success',
                                 'user': user.email,
                                 'url': rev}, status=200)
            else:
                return Response({'detail': 'This account has been disabled.'},
                                status=400)
        else:
            return Response({'detail': 'Incorrect password and '
                                       'username combination.'}, status=400)
    else:
        return Response({'detail': 'Incorrect password and '
                                   'username combination.'}, status=400)


@login_required()
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required()
def email_verification(request, confirmation):
    try:
        try:
            profile = Pleb.get(username=request.user.username,
                               cache_buster=True)
        except DoesNotExist:
            return redirect('logout')
        if token_gen.check_token(request.user, confirmation, profile):
            profile.email_verified = True
            profile.save()
            cache.delete(profile.username)
            return redirect('profile_info')
        else:
            return redirect('401_Error')
    except(CypherException, IOError):
        return redirect('500_Error')


@login_required
@user_passes_test(verify_verified_email,
                  login_url='/registration/signup/confirm/')
def profile_information(request):
    """
    Creates both a AddressInfoForm which populates the
    fields with what the user enters. If this function gets a valid POST
    request it will update the pleb. It then validates the address, through
    smarty streets api, if the address is valid a Address neo_model is
    created and populated.


    COMPLETED THIS TASK BUT STILL NEED TO PUT SOME COMMENTS AROUND IT
    Need to use a hash to verify the same address string is being
    used instead of an int. That way if smarty streets passes back
    the addresses in a different order we can use the same address
    we provided the user previously based on the previous
    smarty streets ordering.
    :param request:
    """
    address_key = settings.ADDRESS_AUTH_ID
    address_information_form = AddressInfoForm(request.POST or None)
    try:
        citizen = Pleb.get(username=request.user.username, cache_buster=True)
    except DoesNotExist:
        return render(request, 'login.html')
    except (CypherException, IOError):
        return redirect('500_Error')
    if citizen.completed_profile_info:
        return redirect("interests")
    if address_information_form.is_valid():
        address_clean = address_information_form.cleaned_data
        address_clean['country'] = 'USA'
        if(address_clean['valid'] == "valid" or
                address_clean.get('original_selected', False) is True):
            try:
                state = dict(US_STATES)[address_clean['state']]
            except KeyError:
                return address_clean['state']
            address = Address(street=address_clean['primary_address'],
                              street_aditional=address_clean[
                                  'street_additional'],
                              city=address_clean['city'],
                              state=state,
                              postal_code=address_clean['postal_code'],
                              latitude=address_clean['latitude'],
                              longitude=address_clean['longitude'],
                              congressional_district=address_clean[
                                  'congressional_district'],
                              county=address_clean['county']).save()
            address.owned_by.connect(citizen)
            citizen.determine_reps()
            spawn_task(task_func=update_address_location,
                       task_param={"object_uuid": address.object_uuid})
            try:
                citizen.completed_profile_info = True
                citizen.save()
                cache.delete(citizen.username)
            except (CypherException, IOError):
                return redirect('500_Error')
            account_type = request.session.get('account_type')
            if account_type is not None:
                return redirect('rep_registration_page')
            return redirect('interests')
        else:
            # TODO this is just a place holder, what should we really be doing
            # here?
            return render(
                request, 'profile_info.html',
                {
                    'address_information_form': address_information_form,
                    "address_key": address_key
                })

    return render(request, 'profile_info.html',
                  {'address_information_form': address_information_form,
                   "address_key": address_key})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def interests(request):
    """
    The interests view creates an InterestForm populates the topics that
    a user can choose from and if a POST request is passed then the function
    checks the validity of the arguments POSTed. If the form is valid then
    the given topics and categories are associated with the logged in user.

    :param request:
    :return: HttpResponse
    """
    interest_form = InterestForm(request.POST or None)
    if interest_form.is_valid():
        if "select_all" in interest_form.cleaned_data:
            interest_form.cleaned_data.pop('select_all', None)
        queries = [('MATCH (pleb:Pleb {username: "%s"}), '
                    '(tag:Tag {name: "%s"}) '
                    'CREATE UNIQUE (pleb)-[:INTERESTED_IN]->(tag) '
                    'RETURN pleb' % (request.user.username, key.lower()), {})
                   for key, value in interest_form.cleaned_data.iteritems()]
        db.cypher_batch_query(queries)
        cache.delete(request.user.username)
        return redirect('profile_picture')

    return render(request, 'interests.html', {'interest_form': interest_form})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def profile_picture(request):
    """
    The profile picture view accepts an image from the user, which is stored in
    the TEMP_FILES directory until it is uploaded to s3 after which the locally
    stored tempfile is deleted. After the url of the image is returned from
    the upload_image util the url is stored as the profile_picture field in
    the Pleb
    model.
`
    :param request:
    :return:
    """
    profile_picture_form = ProfilePictureForm()
    return render(request, 'profile_picture.html',
                  {'profile_picture_form': profile_picture_form})
