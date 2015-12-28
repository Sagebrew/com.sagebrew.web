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

from neomodel import (DoesNotExist, CypherException, db)

from api.utils import spawn_task
from plebs.tasks import send_email_task
from plebs.neo_models import Pleb

from sb_quests.serializers import QuestSerializer
from .forms import (AddressInfoForm, InterestForm,
                    ProfilePictureForm, SignupForm,
                    LoginForm)
from .utils import (verify_completed_registration, verify_verified_email,
                    create_user_util)
from .models import token_gen
from .tasks import update_interests, store_address


def signup_view(request):
    if request.user.is_authenticated() is True:
        user_profile = Pleb.get(username=request.user.username)
        if user_profile.completed_profile_info is True:
            return redirect('newsfeed')
        if not user_profile.email_verified:
            return redirect('confirm_view')
    return render(request, 'sign_up_page/index.html')


def quest_signup(request):
    quest = cache.get('%s_quest' % request.user.username)
    if quest is None:
        query = 'MATCH (pleb:Pleb {username: "%s"})-' \
                '[:IS_WAGING]->(q:Quest) RETURN q' % request.user.username
        res, _ = db.cypher_query(query)
        if res.one:
            return redirect('quest', username=request.user.username)
    if request.method == 'POST':
        if request.user.is_authenticated():
            data = {"account_type": request.POST['account_type']}
            serializer = QuestSerializer(data=data,
                                         context={'request': request})
            if serializer.is_valid():
                quest = serializer.save()
                return redirect('quest', username=quest.owner_username)
            else:
                return redirect('500_Error')
        return redirect('signup')
    return render(request, 'quest_details.html')


@api_view(['POST'])
def signup_view_api(request):
    # DEPRECATED please use Profile Create method and Update Method in
    # plebs/serializers from now on
    quest_registration = request.session.get('account_type')
    try:
        signup_form = SignupForm(request.data)
        valid_form = signup_form.is_valid()
    except AttributeError:
        return Response({'detail': 'Form Error'},
                        status=status.HTTP_400_BAD_REQUEST)
    if valid_form is True:
        if signup_form.cleaned_data['password'] != \
                signup_form.cleaned_data['password2']:
            return Response({'detail': 'Passwords do not match!'},
                            status=status.HTTP_401_UNAUTHORIZED)
        if signup_form.cleaned_data['email'][-4:] == '.gov':
            return Response({"detail": "If you are using a .gov email address "
                                       "please follow this link, or use a "
                                       "personal email address."},
                            status.HTTP_200_OK)
        try:
            test_user = User.objects.get(
                email=signup_form.cleaned_data['email'])
            if test_user.is_active:
                return Response(
                    {'detail': 'A user with this email already exists!'},
                    status=status.HTTP_401_UNAUTHORIZED)
            test_user.is_active = True
            test_user.set_password(signup_form.cleaned_data['password'])
            test_user.save()
            user = authenticate(username=test_user.username,
                                password=signup_form.cleaned_data['password'])
            login(request, user)
            if quest_registration is not None:
                request.session['account_type'] = quest_registration
                request.session.set_expiry(1800)
            return Response({"detail": "existing success"},
                            status=status.HTTP_200_OK)
        except User.DoesNotExist:
            res = create_user_util(first_name=signup_form.
                                   cleaned_data['first_name'],
                                   last_name=signup_form.
                                   cleaned_data['last_name'],
                                   email=signup_form.
                                   cleaned_data['email'],
                                   password=signup_form.
                                   cleaned_data['password'],
                                   birthday=signup_form.
                                   cleaned_data['birthday'])
            if res and res is not None:
                user = authenticate(username=res['username'],
                                    password=signup_form.cleaned_data[
                                        'password'])
            else:
                return Response({'detail': 'system error'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if quest_registration is not None:
                        request.session['account_type'] = quest_registration
                        request.session.set_expiry(1800)
                    return Response({'detail': 'success'},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'account disabled'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'invalid login'},
                                status=status.HTTP_400_BAD_REQUEST)
        except MultipleObjectsReturned:
            return Response({'detail': 'Appears we have two users with '
                                       'that email. Please contact '
                                       'support@sagebrew.com.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"detail": signup_form.errors.as_json()},
                        status=status.HTTP_400_BAD_REQUEST)


def login_view(request):
    try:
        if request.user.is_authenticated() is True:
            return redirect('root_profile_page')
    except AttributeError:
        pass
    return render(request, 'login.html')


@login_required()
def resend_email_verification(request):
    profile = cache.get(request.user.username)
    if profile is None:
        try:
            profile = Pleb.nodes.get(username=request.user.username)
            cache.set(request.user.username, profile)
        except(Pleb.DoesNotExist, DoesNotExist):
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
        profile = Pleb.get(request.user.username)
        if token_gen.check_token(request.user, confirmation, profile):
            profile.email_verified = True
            profile.save()
            profile.refresh()
            cache.set(profile.username, profile)
            return redirect('profile_info')
        else:
            return redirect('401_Error')
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect('logout')
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
    citizen = cache.get(request.user.username)
    if citizen is None:
        try:
            citizen = Pleb.nodes.get(username=request.user.username)
            cache.set(request.user.username, citizen)
        except(Pleb.DoesNotExist, DoesNotExist):
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
            success = spawn_task(store_address,
                                 {"username": request.user.username,
                                  "address_clean": address_clean})
            if isinstance(success, Exception):
                return redirect('500_Error')
            try:
                citizen.completed_profile_info = True
                citizen.save()
                citizen.refresh()
                cache.set(citizen.username, citizen)
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
        data = {"username": request.user.username,
                "interests": interest_form.cleaned_data}
        success = spawn_task(update_interests, data)
        if isinstance(success, Exception):
            return redirect('500_Error')
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
    profile = cache.get(request.user.username)
    if profile is None:
        try:
            profile = Pleb.nodes.get(username=request.user.username)
            cache.set(request.user.username, profile)
        except(Pleb.DoesNotExist, DoesNotExist):
            return render(request, 'login.html')
        except (CypherException, IOError):
            return redirect('500_Error')
    profile_picture_form = ProfilePictureForm()
    return render(
        request, 'profile_picture.html',
        {
            'profile_picture_form': profile_picture_form,
            'pleb': profile
        })
