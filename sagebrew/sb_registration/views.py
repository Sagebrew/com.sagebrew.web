from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseServerError)
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import get_template
from django.template import Context

from rest_framework.decorators import api_view
from rest_framework.response import Response

from neomodel import (DoesNotExist, CypherException)

from api.utils import spawn_task
from plebs.tasks import send_email_task, create_beta_user
from plebs.neo_models import Pleb, BetaUser

from .forms import (AddressInfoForm, InterestForm,
                    ProfilePictureForm, SignupForm,
                    LoginForm, BetaSignupForm)
from .utils import (verify_completed_registration, verify_verified_email,
                    create_user_util)
from .models import token_gen
from .tasks import update_interests, store_address


def signup_view(request):
    if (request.user.is_authenticated() is True and
            verify_completed_registration(request.user) is True):
        return redirect('profile_page', pleb_username=request.user.username)
    user = request.GET.get('user', '')
    if not user:
        return redirect('beta_page')
    try:
        beta_user = BetaUser.nodes.get(email=user)
    except (BetaUser.DoesNotExist, DoesNotExist, CypherException, IOError):
        return redirect('beta_page')
    if not beta_user.invited:
        return redirect('beta_page')

    return render(request, 'sign_up_page/index.html')


def quest_signup(request):
    return render(request, 'quest_signup.html')


@api_view(['POST'])
def signup_view_api(request):
    try:
        signup_form = SignupForm(request.DATA)
        valid_form = signup_form.is_valid()
    except AttributeError:
        return Response({'detail': 'Form Error'}, status=400)
    if valid_form is True:
        if signup_form.cleaned_data['password'] != \
                signup_form.cleaned_data['password2']:
            return Response({'detail': 'Passwords do not match!'},
                            status=401)
        if signup_form.cleaned_data['email'][-4:] == '.gov':
            return Response({"detail": "If you are using a .gov email address "
                                       "please follow this link, or use a "
                                       "personal email address."}, 200)
        try:
            User.objects.get(email=signup_form.cleaned_data['email'])
            return Response(
                {'detail': 'A user with this email already exists!'},
                status=401)
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
                return Response({'detail': 'system error'}, status=500)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return Response({'detail': 'success'}, status=200)
                else:
                    return Response({'detail': 'account disabled'},
                                    status=400)
            else:
                return Response({'detail': 'invalid login'},
                                status=400)
    else:
        return Response({"detail": signup_form.errors.as_json()},
                        status=400)


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
            return HttpResponse('Server Error', status=500)

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
        # TODO need to replace this with an actual view
        return HttpResponseServerError("Unhandled Exception Occurred")
    return redirect("confirm_view")


@api_view(['POST'])
def login_view_api(request):
    try:
        login_form = LoginForm(request.DATA)
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
        user = authenticate(username=user.username,
                            password=login_form.cleaned_data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                rev = reverse('profile_page',
                              kwargs={'pleb_username': user.username})
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
            # TODO Ensure to link up to a real redirect page
            return HttpResponse('Unauthorized', status=401)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect('logout')
    except(CypherException, IOError):
        # TODO Actually redirect to 500 page
        return HttpResponse('Server Error', status=500)


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
            return HttpResponse('Server Error', status=500)
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
                return HttpResponseServerError('Server Error')
            try:
                citizen.completed_profile_info = True
                citizen.save()
                citizen.refresh()
                cache.set(citizen.username, citizen)
            except (CypherException, IOError):
                # TODO instead of going to 500 we should instead repopulate the
                # page with the forms and make an alert or notification that
                # indicates we're sorry but there was an error communicating
                # with the server.
                return HttpResponseServerError('Server Error')
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
            return HttpResponse('Server Error', status=500)
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
            return HttpResponse('Server Error', status=500)
    profile_picture_form = ProfilePictureForm()
    return render(
        request, 'profile_picture.html',
        {
            'profile_picture_form': profile_picture_form,
            'pleb': profile
        })


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def quest_registration(request):
    return render(request, 'position_selection.html')


@api_view(['POST'])
def beta_signup(request):
    beta_form = BetaSignupForm(request.DATA or None)
    if beta_form.is_valid() is True:
        try:
            BetaUser.nodes.get(email=beta_form.cleaned_data["email"])
            return Response({"detail": "Beta User Already Exists"}, 409)
        except (BetaUser.DoesNotExist, DoesNotExist):
            res = spawn_task(create_beta_user, beta_form.cleaned_data)
            if isinstance(res, Exception):
                return Response({"detail": "Server Error"}, 500)
            return Response({"detail": "success"}, 200)
        except (CypherException, IOError):
            return Response({"detail": "Server Error"}, 500)
    else:
        return Response({"detail": beta_form.errors.as_json()}, 400)


def beta_page(request):
    if request.user.is_authenticated() is True:
        if verify_completed_registration(request.user) is True:
            return redirect('profile_page', pleb_username=request.user.username)
        else:
            return redirect('profile_info')

    return render(request, "beta.html")
