import stripe
from django.conf import settings
from uuid import uuid1
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseNotFound,
                         HttpResponseServerError)
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
from sb_reps.tasks import create_rep_task
from sb_docstore.tasks import build_rep_page_task
from sb_uploads.tasks import crop_image_task

from .forms import (ProfileInfoForm, AddressInfoForm, InterestForm,
                    ProfilePictureForm, SignupForm, RepRegistrationForm,
                    LoginForm, BetaSignupForm)
from .utils import (upload_image, verify_completed_registration,
                    verify_verified_email, calc_age,
                    create_user_util)
from .models import token_gen
from .tasks import update_interests, store_address


def signup_view(request):
    user = request.GET.get('user', '')
    if not user:
        return redirect('beta_page')
    try:
        beta_user = BetaUser.nodes.get(email=user)
    except (BetaUser.DoesNotExist, DoesNotExist, CypherException):
        return redirect('beta_page')
    if not beta_user.invited:
        return redirect('beta_page')
    return render(request, 'sign_up_page/index.html')

@api_view(['POST'])
def signup_view_api(request):
    try:
        signup_form = SignupForm(request.DATA)
        valid_form = signup_form.is_valid()
    except AttributeError:
        return Response(status=400)
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
    return render(request, 'login.html')


@login_required()
def resend_email_verification(request):
    try:
        pleb = Pleb.nodes.get(email=request.user.email)
    except(DoesNotExist):
        return HttpResponseNotFound("Could not find user")

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
            return Response({'detail': 'cannot find user'}, status=400)
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
    try:
        citizen = Pleb.nodes.get(email=request.user.email)
    except (Pleb.DoesNotExist, DoesNotExist):
        return redirect("404_Error")
    except (CypherException, IOError) as e:
        return HttpResponseServerError('Server Error')
    if citizen.completed_profile_info:
        return redirect("interests")
    if profile_information_form.is_valid():
        citizen.home_town = profile_information_form.cleaned_data["home_town"]
        #citizen.high_school = profile_information_form.cleaned_data.get(
        #   "high_school", "")
        #citizen.college = profile_information_form.cleaned_data.get(
        #    "college", "")
        #citizen.employer = profile_information_form.cleaned_data.get(
        #    "employer", "")
        citizen.save()
    if address_information_form.is_valid():
        address_clean = address_information_form.cleaned_data
        address_clean['country'] = 'USA'
        if(address_clean['valid'] == "valid" or
                   address_clean.get('original_selected', False) is True):
            success = spawn_task(store_address,
                                 {"address_clean": address_clean})
            if isinstance(success, Exception):
                return HttpResponseServerError('Server Error')
            try:
                citizen.completed_profile_info = True
                citizen.save()
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
            return render(request, 'profile_info.html',
                  {'profile_information_form': profile_information_form,
                   'address_information_form': address_information_form})

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
        data = {"email": request.user.email,
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
        print request.POST, request.FILES
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES)
        if profile_picture_form.is_valid():
            print profile_picture_form.cleaned_data
            image_uuid = str(uuid1())
            data = request.FILES['picture']
            image_data = {
                "image": data,
                "x": profile_picture_form.cleaned_data['image_x1'],
                "y": profile_picture_form.cleaned_data['image_y1'],
                "width": profile_picture_form.cleaned_data['image_x2'],
                "height": profile_picture_form.cleaned_data['image_y2'],
                "f_uuid": image_uuid
            }
            res = spawn_task(crop_image_task, image_data)
            if isinstance(res, Exception):
                return HttpResponse('Server Error', status=500)

            #citizen.profile_pic = upload_image(
                #settings.AWS_PROFILE_PICTURE_FOLDER_NAME, image_uuid, data)
            #citizen.profile_pic_uuid = image_uuid
            #citizen.save()
            return redirect('profile_page', pleb_username=citizen.username)
    else:
        profile_picture_form = ProfilePictureForm()
    return render(request, 'profile_picture.html',
                  {'profile_picture_form': profile_picture_form,
                   'pleb': citizen})


@login_required()
@user_passes_test(verify_completed_registration,
                  login_url='/registration/profile_information')
def rep_reg_page(request):
    uuid = str(uuid1())
    customer_id = None
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        reg_form = RepRegistrationForm(request.POST)
        valid_form = reg_form.is_valid()
        if valid_form:
            cleaned = reg_form.cleaned_data
            if cleaned['account_type'] == 'sub':
                customer = stripe.Customer.create(
                    description="Customer for %s" % cleaned['account_name'],
                    card=cleaned['stripeCardToken']
                )
                customer_id = customer['id']
            recipient = stripe.Recipient.create(
                name=cleaned['account_name'],
                tax_id=cleaned['ssn'],
                type="individual",
                bank_account=cleaned['stripeBankToken'],
                email=cleaned['gov_email']
            )
            recipient_id = recipient['id']
            task_data = {
                'pleb_username': request.user.username,
                'rep_type': cleaned['office'],
                'rep_id': uuid,
                'customer_id': customer_id,
                'recipient_id': recipient_id
            }
            res = spawn_task(create_rep_task, task_data)
            if isinstance(res, Exception):
                return redirect("404_Error")
            res = spawn_task(build_rep_page_task, {'rep_id': uuid,
                                                   'rep_type': cleaned[
                                                       'office']})
            if isinstance(res, Exception):
                return
            return redirect("rep_page", rep_type=cleaned['office'], rep_id=uuid)
    return render(request, 'registration_rep.html')


@api_view(['POST'])
def beta_signup(request):
    beta_form = BetaSignupForm(request.DATA or None)
    if beta_form.is_valid():
        res = spawn_task(create_beta_user, beta_form.cleaned_data)
        if isinstance(res, Exception):
            return Response({"detail": "Failed to spawn task"}, 500)
        return Response({"detail": "success"}, 200)
    else:
        return Response({"detail": beta_form.errors.as_json()}, 400)