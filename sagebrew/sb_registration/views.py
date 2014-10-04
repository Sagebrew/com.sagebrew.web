import shortuuid
import logging
import hashlib
from json import loads
from django.conf import settings
from uuid import uuid1
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string, get_template
from django.template import Context
from rest_framework.decorators import api_view
from rest_framework.response import Response

from plebs.neo_models import Pleb, TopicCategory, SBTopic, Address
from .forms import (ProfileInfoForm, AddressInfoForm, InterestForm,
                    ProfilePictureForm, AddressChoiceForm, SignupForm,
                    LoginForm)
from .utils import (validate_address, generate_interests_tuple, upload_image,
                    compare_address, generate_address_tuple,
                    create_address_string,
                    create_address_long_hash, verify_completed_registration,
                    verify_verified_email)
from .models import EmailAuthTokenGenerator

logger = logging.getLogger('loggly_logs')
token_gen = EmailAuthTokenGenerator()

@login_required()
def confirm_view(request):
    return render(request, 'verify_email.html')

def signup_view(request):
    return render(request, 'sign_up_page/index.html')

@api_view(['POST'])
def signup_view_api(request):
    try:
        signup_form = SignupForm(loads(request.body))
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
                user = User.objects.create_user(first_name=signup_form.
                                                cleaned_data['first_name'],
                                                last_name=signup_form.
                                                cleaned_data['last_name'],
                                                email=signup_form.
                                                cleaned_data['email'],
                                                username=shortuuid.uuid(),
                                                password=signup_form.
                                                cleaned_data['password'])
                user.save()
                user = authenticate(username=user.username,
                                    password=signup_form.cleaned_data[
                                        'password'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        template_dict = {
                            'full_name': request.user.first_name+' '+request.user.last_name,
                            'verification_url': settings.EMAIL_VERIFICATION_URL+token_gen.make_token(user)+'/'
                        }
                        subject, to = "Sagebrew Email Verification", request.user.email
                        text_content = get_template('email_templates/email_verification.txt').render(Context(template_dict))
                        html_content = get_template('email_templates/email_verification.html').render(Context(template_dict))
                        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to])
                        msg.attach_alternative(html_content, 'text/html')
                        msg.send()
                        return Response({'detail': 'success'}, status=200)
                    else:
                        return Response({'detail': 'account disabled'},
                                        status=400)
                else:
                    return Response({'detail': 'invalid login'},
                                    status=400)
    except Exception:
        logger.exception({'function': signup_view_api.__name__,
                          'exception': 'UnhandledException: '})
        return Response({'detail': 'exception'}, status=400)

def login_view(request):
    return render(request, 'login.html')

@login_required()
def resend_email_verification(request):
    try:
        template_dict = {
            'full_name': request.user.first_name+' '+request.user.last_name,
            'verification_url': settings.EMAIL_VERIFICATION_URL+token_gen.make_token(request.user)+'/'
        }
        subject, to = "Sagebrew Email Verification", request.user.email
        text_content = get_template('email_templates/email_verification.txt').render(Context(template_dict))
        html_content = get_template('email_templates/email_verification.html').render(Context(template_dict))
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [to])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        return redirect("confirm_view")
    except Pleb.DoesNotExist:
        logger.exception({'function': resend_email_verification.__name__,
                          'exception': 'DoesNotExist: '})
        return Response({'detail': 'pleb does not exist'}, status=400)

@api_view(['POST'])
def login_view_api(request):
    try:
        login_form = LoginForm(loads(request.body))
        if login_form.is_valid():
            user = User.objects.get(email=login_form.cleaned_data['email'])
            user = authenticate(username=user.username,
                                password=login_form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    pleb = Pleb.nodes.get(email=user.email)
                    pleb.generate_username()
                    profile_page_url = settings.WEB_ADDRESS+'/user/'+pleb.username
                    return Response({'detail': 'success',
                                     'user': user.email,
                                     'url': profile_page_url}, status=200)
                else:
                    return Response({'detail': 'account disabled'},
                                    status=400)
            else:
                return Response({'detail': 'invalid password'}, status=200)
    except User.DoesNotExist:
        logger.exception({'detail': 'cannot find user',
                          'exception': 'User.DoesNotExist'})
        return Response({'detail': 'cannot find user'}, status=200)
    except Exception:
        logger.exception({'function': login_view_api.__name__,
                          'exception': 'UnhandledException: '})
        return Response({'detail': 'unknown exception'}, status=400)

@login_required()
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required()
def email_verification(request, confirmation):
    try:
        pleb = Pleb.nodes.get(email=request.user.email)
        if token_gen.check_token(request.user, confirmation):
            pleb.email_verified = True
            pleb.save()
            return redirect('profile_info')
        else:
            return redirect('confirm_view')
    except Pleb.DoesNotExist:
        logger.exception({'function': email_verification.__name__,
                          'exception': 'DoesNotExist: '})
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
    # TODO Add custom logic after State is submitted that checks if the
    # entered value is within the 50 states
    # if not return error indicating sorry we currently only support 50
    profile_information_form = ProfileInfoForm(request.POST or None)
    address_information_form = AddressInfoForm(request.POST or None)
    address_selection_form = AddressChoiceForm(request.POST or None)
    address_selection = "no_selection"
    try:
        citizen = Pleb.nodes.get(email=request.user.email)
    except Pleb.DoesNotExist:
        return redirect("404_Error")
    if profile_information_form.is_valid():
        citizen.date_of_birth = profile_information_form.cleaned_data[
            "date_of_birth"]
        citizen.home_town = profile_information_form.cleaned_data["home_town"]
        citizen.high_school = profile_information_form.cleaned_data[
            "high_school"]
        citizen.college = profile_information_form.cleaned_data["college"]
        citizen.employer = profile_information_form.cleaned_data["employer"]
        citizen.save()

    if address_information_form.is_valid():
        address_clean = address_information_form.cleaned_data
        address_info = validate_address(address_clean)
        if not address_info:
            address = Address(address_hash=str(uuid1()),
                              street=address_clean['primary_address'],
                              street_additional=address_clean['street_additional'],
                              city=address_clean['city'],
                              state=address_clean['state'],
                              postal_code=address_clean['postal_code'],
                              validated=False)
            address.save()
            address.address.connect(citizen)
            citizen.address.connect(address)
            citizen.completed_profile_info = True
            citizen.save()
            return redirect('interests')
        addresses_returned = len(address_info)
        address_tuple = generate_address_tuple(address_info)

        # Not doing 0 cause already done with address_information_form
        if (addresses_returned == 1):
            if compare_address(address_info[0], address_clean):
                address_info[0]["country"] = "USA"
                address_long_hash = create_address_long_hash(
                    address_info[0])
                try:
                    address = Address.nodes.get(address_hash=address_long_hash)
                except Address.DoesNotExist:
                    address_info[0]["address_hash"] = address_long_hash
                    address = Address(**address_info[0])
                    address.save()
                address.address.connect(citizen)
                citizen.completed_profile_info = True
                citizen.address.connect(address)
                citizen.save()
                return redirect('interests')
            else:
                address_selection_form.fields[
                    'address_options'].choices = address_tuple
                address_selection_form.fields[
                    'address_options'].required = True
                address_selection = "selection"
        elif (addresses_returned > 1):
            # Choices need to be populated prior to is_valid call to ensure
            # that the form validates against the correct values
            # We also are able ot keep this in the same location because
            # we hid the other address form but it keeps the same values as
            # previously entered. This enables us to get the same results
            # back from smarty streets and validate those choices again then
            # select the one that the user selected.
            address_selection_form.fields[
                'address_options'].choices = address_tuple
            address_selection_form.fields['address_options'].required = True
            address_selection = "selection"

        if (address_selection == "selection"):
            if (address_selection_form.is_valid()):
                store_address = None
                address_hash = address_selection_form.cleaned_data[
                    "address_options"]
                for optional_address in address_info:
                    optional_address["country"] = "USA"
                    address_string = create_address_string(optional_address)
                    optional_hash = hashlib.sha224(address_string).hexdigest()
                    if (address_hash == optional_hash):
                        store_address = optional_address
                        break
                if (store_address is not None):
                    address_long_hash = create_address_long_hash(store_address)
                    try:
                        address = Address.nodes.get(
                            address_hash=address_long_hash)
                    except Address.DoesNotExist:
                        store_address["address_hash"] = address_long_hash
                        address = Address(**store_address)
                        address.save()
                    address.address.connect(citizen)
                    citizen.completed_profile_info = True
                    citizen.address.connect(address)
                    citizen.save()
                    return redirect('interests')

    return render(request, 'profile_info.html',
                  {'profile_information_form': profile_information_form,
                   'address_information_form': address_information_form,
                   'address_selection': address_selection,
                   'address_choice_form': address_selection_form})


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
    choices_tuple = generate_interests_tuple()
    interest_form.fields["specific_interests"].choices = choices_tuple
    if interest_form.is_valid():
        for item in interest_form.cleaned_data:
            if (interest_form.cleaned_data[item] and
                        item != "specific_interests"):
                try:
                    citizen = Pleb.nodes.get(email=request.user.email)
                    # TODO profile page profile picture
                    if citizen.completed_profile_info:
                        return redirect('profile_picture')
                except Pleb.DoesNotExist:
                    redirect("404_Error")
                try:
                    category_object = TopicCategory.nodes.get(
                        title=item.capitalize())
                    for topic in category_object.sb_topics.all():
                        # citizen.sb_topics.connect(topic)
                        pass
                        # citizen.topic_category.connect(category_object)
                except TopicCategory.DoesNotExist:
                    redirect("404_Error")

        for topic in interest_form.cleaned_data["specific_interests"]:
            try:
                interest_object = SBTopic.nodes.get(title=topic)
            except SBTopic.DoesNotExist:
                redirect("404_Error")
                # citizen.sb_topics.connect(interest_object)
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

