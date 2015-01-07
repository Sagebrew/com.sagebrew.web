from django.conf import settings
from uuid import uuid1
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import get_template
from django.template import Context
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from neomodel import (DoesNotExist, AttemptedCardinalityViolation,
                      CypherException)

from sb_tag.neo_models import SBTag
from api.utils import spawn_task
from plebs.tasks import send_email_task
from plebs.neo_models import Pleb, Address

from .forms import (ProfileInfoForm, AddressInfoForm, InterestForm,
                    ProfilePictureForm, SignupForm,
                    LoginForm)
from .utils import (upload_image,
                    create_address_long_hash, verify_completed_registration,
                    verify_verified_email, calc_age,
                    create_user_util)
from .models import token_gen


@api_view(['POST'])
def signup_view_api(request):
    try:
        signup_form = SignupForm(request.DATA)
        valid_form = signup_form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form:
        if signup_form.cleaned_data['password'] != \
                signup_form.cleaned_data['password2']:
            return Response({'detail': 'Passwords do not match!'},
                            status=401)
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
                                   cleaned_data['password'])
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
        return Response({'detail': "invalid form"}, status=400)


def login_view(request):
    return render(request, 'login.html')


@login_required()
def resend_email_verification(request):
    try:
        pleb = Pleb.nodes.get(email=request.user.email)
    except(DoesNotExist):
        return Response({'detail': 'pleb does not exist'}, status=400)

    template_dict = {
        'full_name': request.user.get_full_name(),
        'verification_url': "%s%s%s" % (settings.EMAIL_VERIFICATION_URL,
                                        token_gen.make_token(
                                            request.user, pleb),
                                        '/')
    }
    subject, to = "Sagebrew Email Verification", request.user.email
    # text_content = get_template(
    # 'email_templates/email_verification.txt').render(Context(template_dict))
    html_content = get_template(
        'email_templates/email_verification.html').render(
        Context(template_dict))
    task_data = {'to': to, 'subject': subject, 'html_content': html_content}
    spawned = spawn_task(task_func=send_email_task, task_param=task_data)
    if isinstance(spawned, Exception):
        # TODO need to replace this with an actual view
        return Response(status=500)
    return redirect("confirm_view")


@api_view(['POST'])
def login_view_api(request):
    try:
        login_form = LoginForm(request.DATA)
        valid_form = login_form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form:
        try:
            user = User.objects.get(email=login_form.cleaned_data['email'])
        except User.DoesNotExist:
            return Response({'detail': 'cannot find user'}, status=400)
        user = authenticate(username=user.username,
                            password=login_form.cleaned_data['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                # TODO do we need this logic? If we can get away with
                # loading the page based on the user.email and user.username
                # we should try. Then we can query the pleb when we
                # get to their page and build their document storage up
                # if it's not already built
                try:
                    pleb = Pleb.nodes.get(email=user.email)
                except (Pleb.DoesNotExist, DoesNotExist):
                    return Response({'detail': 'cannot find user'},
                                    status=400)

                rev = reverse('profile_page',
                              kwargs={'pleb_username': pleb.username})
                return Response({'detail': 'success',
                                 'user': user.email,
                                 'url': rev}, status=200)
            else:
                return Response({'detail': 'account disabled'},
                                status=400)
        else:
            return Response({'detail': 'invalid password'}, status=400)
    else:
        return Response({'detail': 'invalid form'}, status=400)

@login_required()
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required()
def email_verification(request, confirmation):
    try:
        pleb = Pleb.nodes.get(email=request.user.email)
        if token_gen.check_token(request.user, confirmation, pleb):
            pleb.email_verified = True
            pleb.save()
            return redirect('profile_info')
        else:
            # TODO Ensure to link up to a real redirect page
            return HttpResponse('Unauthorized', status=401)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect('logout')
    except(CypherException):
        # TODO Actually redirect to 500 page
        return HttpResponse('Server Error', status=500)


@login_required
@user_passes_test(verify_verified_email,
                  login_url='/registration/signup/confirm/')
def profile_information(request):
    '''
    Creates both a ProfileInfoForm and AddressInfoForm which populates the
    fields with what the user enters. If this function gets a valid POST
    request it
    will update the pleb. It then validates the address, through
    smartystreets api,
    if the address is valid a Address neo_model is created and populated.


    COMPLETED THIS TASK BUT STILL NEED TO PUT SOME COMMENTS AROUND IT
    Need to use a hash to verify the same address string is being
    used instead of an int. That way if smarty streets passes back
    the addresses in a different order we can use the same address
    we provided the user previously based on the previous
    smarty streets ordering.
    '''
    profile_information_form = ProfileInfoForm(request.POST or None)
    address_information_form = AddressInfoForm(request.POST or None)
    # TODO can we use the base user here rather than querying for the pleb?
    # Also I think we can move the address storage logic into a task and follow
    # a similar process as described with the profile picture where we're
    # really just building up the plebs personal document with these
    # and spawning off tasks in the background to store the information
    # in neo
    try:
        citizen = Pleb.nodes.get(email=request.user.email)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    if citizen.completed_profile_info:
        return redirect("interests")
    if profile_information_form.is_valid():
        citizen.home_town = profile_information_form.cleaned_data["home_town"]
        #citizen.high_school = profile_information_form.cleaned_data.get("high_school", "")
        #citizen.college = profile_information_form.cleaned_data.get("college", "")
        #citizen.employer = profile_information_form.cleaned_data.get("employer", "")
        citizen.save()
    if address_information_form.is_valid():
        address_clean = address_information_form.cleaned_data
        address_clean['country'] = 'USA'
        if address_clean['valid']=="valid":
            address_hash = create_address_long_hash(address_clean)
            try:
                address = Address.nodes.get(address_hash=address_hash)
            except (Address.DoesNotExist, DoesNotExist):
                address = Address(address_hash=address_hash,
                                  street=address_clean['primary_address'],
                                  street_aditional=address_clean[
                                      'street_additional'],
                                  city=address_clean['city'],
                                  state=address_clean['state'],
                                  postal_code=address_clean['postal_code'],
                                  latitude=address_clean['latitude'],
                                  longitude=address_clean['longitude'],
                                  congressional_district=address_clean[
                                      'congressional_district'])
                address.save()
            address.address.connect(citizen)
            try:
                citizen.address.connect(address)
            except AttemptedCardinalityViolation:
                return redirect('interests')
            citizen.completed_profile_info = True
            citizen.save()
            return redirect('interests')
        elif address_clean['valid']=="invalid" and \
                address_clean['original_selected']:
            address = Address(address_hash=str(uuid1()),
                              street=address_clean['primary_address'],
                              street_additional=address_clean[
                                  'street_additional'],
                              city=address_clean['city'],
                              state=address_clean['state'],
                              postal_code=address_clean['postal_code'],
                              latitude=address_clean['latitude'],
                              longitude=address_clean['longitude'],
                              congressional_district=address_clean[
                                  'congressional_district'],
                              validated = False)
            address.save()
            address.address.connect(citizen)
            try:
                citizen.address.connect(address)
            except AttemptedCardinalityViolation:
                return redirect('interests')
            citizen.completed_profile_info = True
            citizen.save()
            return redirect('interests')

    return render(request, 'profile_info.html',
                  {'profile_information_form': profile_information_form,
                   'address_information_form': address_information_form})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def interests(request):
    '''
    The interests view creates an InterestForm populates the topics that
    a user can choose from and if a POST request is passed then the function
    checks the validity of the arguments POSTed. If the form is valid then
    the given topics and categories are associated with the logged in user.

    :param request:
    :return: HttpResponse
    '''
    interest_form = InterestForm(request.POST or None)
    if interest_form.is_valid():
        # TODO can we use the base user here rather than
        # querying for the pleb? Then spawn a task for connecting the
        # interests
        try:
            citizen = Pleb.nodes.get(email=request.user.email)
        except (Pleb.DoesNotExist, DoesNotExist):
            return redirect("404_Error")
        except CypherException:
            return HttpResponse('Server Error', status=500)
        for item in interest_form.cleaned_data:
            if interest_form.cleaned_data[item]:
                try:
                    tag = SBTag.nodes.get(tag_name=item)
                    citizen.interests.connect(tag)
                except (SBTag.DoesNotExist, DoesNotExist):
                    return redirect("404_Error")
                except CypherException:
                    return HttpResponse('Server Error', status=500)
        return redirect('profile_picture')

    return render(request, 'interests.html', {'interest_form': interest_form})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def profile_picture(request):
    '''
    The profile picture view accepts an image from the user, which is stored in
    the TEMP_FILES directory until it is uploaded to s3 after which the locally
    stored tempfile is deleted. After the url of the image is returned from
    the upload_image util the url is stored as the profile_picture field in
    the Pleb
    model.
`
    :param request:
    :return:
    '''
    # TODO can we use the base user here rather than querying for the pleb?
    # Then spawn a task to connect the profile pic? We'll want to save the image
    # as quickly as possible so it's available but maybe we do that with the
    # new document store, save it into the pleb's document quickly and then
    # spawn off a task for storing the url in neo and working with blitline to
    # get different versions of the image.
    try:
        citizen = Pleb.nodes.get(email=request.user.email)
    except(Pleb.DoesNotExist, DoesNotExist):
        return render(request, 'login.html')
    except CypherException:
        return HttpResponse('Server Error', status=500)
    if request.method == 'POST':
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES)

        if profile_picture_form.is_valid():
            image_uuid = str(uuid1())
            data = request.FILES['picture']
            citizen.profile_pic = upload_image(
                settings.AWS_PROFILE_PICTURE_FOLDER_NAME, image_uuid, data)
            citizen.profile_pic_uuid = image_uuid
            citizen.save()
            return redirect('profile_page', pleb_username=citizen.username)
    else:
        profile_picture_form = ProfilePictureForm()
    return render(request, 'profile_picture.html',
                  {'profile_picture_form': profile_picture_form,
                   'pleb': citizen})

@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def rep_stripe_page(request):
    pass

