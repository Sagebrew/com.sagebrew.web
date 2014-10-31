import logging
from django.conf import settings
from uuid import uuid1
from json import dumps
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import get_template
from django.template import Context
from rest_framework.decorators import api_view
from rest_framework.response import Response
from neomodel import DoesNotExist, AttemptedCardinalityViolation

from sb_tag.neo_models import SBTag
from api.utils import spawn_task
from plebs.tasks import send_email_task
from plebs.neo_models import Pleb, TopicCategory, SBTopic, Address
from .forms import (ProfileInfoForm, AddressInfoForm, InterestForm,
                    ProfilePictureForm, SignupForm,
                    LoginForm)
from .utils import (upload_image,
                    create_address_long_hash, verify_completed_registration,
                    verify_verified_email, calc_age,
                    create_user_util)
from .models import token_gen

logger = logging.getLogger('loggly_logs')


@login_required()
def confirm_view(request):
    return render(request, 'verify_email.html')

def signup_view(request):
    # TODO Need to take the user somewhere and do something with the ajax
    # from the api.
    # Need to take them to a 500 error page or something.
    # Otherwise they just sit at the sign up page
    # with the button not taking them anywhere.
    return render(request, 'sign_up_page/index.html')

@api_view(['POST'])
def signup_view_api(request):
    try:
        try:
            signup_form = SignupForm(request.DATA)
        except TypeError:
            return Response(status=400)
        if signup_form.is_valid():
            if signup_form.cleaned_data['password'] != \
                    signup_form.cleaned_data['password2']:
                return Response({'detail': 'Passwords do not match!'},
                                status=401)
            try:
                test_user = User.objects.get(email=signup_form.
                                             cleaned_data['email'])
                return Response({'detail':
                                     'A user with this email already exists!'},
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
                # TODO if this fails we might want to roll back the user creation
                # Otherwise we end up creating a user and never actually moving
                # the user forward. Then when they go to try again they get
                # a user already exists error
                # Also need to benchmark process in production/staging
                # on local instance with docker after clicking sign up the
                # user sits at the page for a couple seconds prior to being
                # redirected. This makes it seem as though nothing happened on
                # click. They click again and it results in an error being provided.
                # We may have to do a loading greyed out screen while waiting
                # for a response if the timing takes that long in prod.
                # Or go over to a pure view implementation without the API.
                # Just need to look into it when not going through so many
                # different hops
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
        # TODO add a handler for if the form is not valid
    except Exception:
        logger.exception(dumps({'function': signup_view_api.__name__,
                                'exception': 'UnhandledException'}))
        return Response({'detail': 'exception'}, status=400)

def login_view(request):
    return render(request, 'login.html')

@login_required()
def resend_email_verification(request):
    try:
        pleb = Pleb.nodes.get(email=request.user.email)
    except (Pleb.DoesNotExist, DoesNotExist):
        return Response({'detail': 'pleb does not exist'}, status=400)

    template_dict = {
        'full_name': request.user.first_name+' '+request.user.last_name,
        'verification_url': settings.EMAIL_VERIFICATION_URL+token_gen.make_token(request.user, pleb)+'/'
    }
    subject, to = "Sagebrew Email Verification", request.user.email
    text_content = get_template('email_templates/email_verification.txt').render(Context(template_dict))
    html_content = get_template('email_templates/email_verification.html').render(Context(template_dict))
    task_data = {'to': to, 'subject': subject, 'text_content': text_content,
                 'html_content': html_content}
    spawn_task(task_func=send_email_task, task_param=task_data)
    return redirect("confirm_view")


@api_view(['POST'])
def login_view_api(request):
    try:
        try:
            login_form = LoginForm(request.DATA)
        except TypeError:
            return Response(status=400)
        if login_form.is_valid():
            try:
                user = User.objects.get(email=login_form.cleaned_data['email'])
            except User.DoesNotExist:
                return Response({'detail': 'cannot find user'}, status=400)
            user = authenticate(username=user.username,
                                password=login_form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    try:
                        pleb = Pleb.nodes.get(email=user.email)
                    except (Pleb.DoesNotExist, DoesNotExist):
                        return Response({'detail': 'cannot find user'},
                                        status=400)
                    pleb.generate_username()
                    rev = reverse('profile_page',
                                  kwargs={'pleb_email': pleb.email})
                    profile_page_url = settings.WEB_ADDRESS+rev
                    return Response({'detail': 'success',
                                     'user': user.email,
                                     'url': profile_page_url}, status=200)
                else:
                    return Response({'detail': 'account disabled'},
                                    status=400)
            else:
                return Response({'detail': 'invalid password'}, status=400)
    except Exception:
        logger.exception(dumps({'function': login_view_api.__name__,
                                'exception': 'UnhandledException'}))
        return Response({'detail': 'unknown exception'}, status=400)

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
    except Exception:
        logger.exception({'function': email_verification.__name__,
                          'exception': 'UnhandledException: '})
        return redirect('confirm_view')

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

    try:
        citizen = Pleb.nodes.get(email=request.user.email)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    if citizen.completed_profile_info:
        return redirect("interests")
    if profile_information_form.is_valid():
        citizen.date_of_birth = profile_information_form.cleaned_data[
            "date_of_birth"]
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
                                  street_aditional=address_clean['street_additional'],
                                  city=address_clean['city'],
                                  state=address_clean['state'],
                                  postal_code=address_clean['postal_code'],
                                  latitude=address_clean['latitude'],
                                  longitude=address_clean['longitude'],
                                  congressional_district=address_clean['congressional_district'])
                address.save()
            address.address.connect(citizen)
            try:
                citizen.address.connect(address)
            except AttemptedCardinalityViolation:
                return redirect('interests')
            citizen.completed_profile_info = True
            citizen.save()
            return redirect('interests')
        elif address_clean['valid']=="invalid" and address_clean['original_selected']:
            address = Address(address_hash=str(uuid1()),
                              street=address_clean['primary_address'],
                              street_additional=address_clean['street_additional'],
                              city=address_clean['city'],
                              state=address_clean['state'],
                              postal_code=address_clean['postal_code'],
                              latitude=address_clean['latitude'],
                              longitude=address_clean['longitude'],
                              congressional_district=address_clean['congressional_district'],
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
        try:
            citizen = Pleb.nodes.get(email=request.user.email)
        except (Pleb.DoesNotExist, DoesNotExist):
            redirect("404_Error")
        for item in interest_form.cleaned_data:
            if interest_form.cleaned_data[item]:
                try:
                    tag = SBTag.nodes.get(tag_name=item)
                except (SBTag.DoesNotExist, DoesNotExist):
                    redirect("404_Error")
                citizen.interests.connect(tag)
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
    if request.method == 'POST':
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES)
        if profile_picture_form.is_valid():
            try:
                citizen = Pleb.nodes.get(email=request.user.email)
                # if citizen.completed_profile_info:
                #    return redirect('profile_page')
            except Pleb.DoesNotExist:
                return render(request, 'profile_picture.html',
                              {'profile_picture_form': profile_picture_form})
            image_uuid = uuid1()
            data = request.FILES['picture']
            temp_file = '%s%s.jpeg' % (settings.TEMP_FILES, image_uuid)
            with open(temp_file, 'wb+') as destination:
                for chunk in data.chunks():
                    destination.write(chunk)
            citizen.profile_pic = upload_image(settings.AWS_PROFILE_PICTURE_FOLDER_NAME,
                                               image_uuid)
            citizen.profile_pic_uuid = image_uuid
            citizen.save()
            return redirect('profile_page', pleb_email=citizen.email)  #
            # citizen.first_name+'_'+citizen.last_name)
    else:
        profile_picture_form = ProfilePictureForm()
    return render(request, 'profile_picture.html',
                  {'profile_picture_form': profile_picture_form})

