from django.shortcuts import (render_to_response, redirect)
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect

from haystack.forms import SearchForm
from haystack.views import SearchView

from address.forms import AddressSettingsForm

from .forms import AccountSettingsForm
from .utils import ProfileUtils


def unknown_user(request):
    return render_to_response('index.html', {},
                                context_instance=RequestContext(request))

@login_required
def user_profile(request, username):
    '''
    user_profile(Context, String) provides a template with the information
    associated with the user who's page it is with regard to if the user
    who is attempting to access it is the owner, a friend of the user, or a
    stranger.
    '''
    def set_profile_util(user, page_user):
        return ProfileUtils(user, page_user)

    user = request.user
    try:
        page_user = User.objects.get(username=username)
    except(User.DoesNotExist):
        return redirect(unknown_user)

    if(user != None and page_user != None):
        profile_util = set_profile_util(user, page_user)
    else:
        raise Http404

    data = profile_util.page_data()
    return render_to_response(data['template'], data['return_dict'],
               RequestContext(request))


@login_required
def home_profile(request):
    response = user_profile(request, request.user.username)
    return response

@login_required
def standard_settings(request):
    user = User.objects.get(username=request.user)
    if request.method == 'POST':
        standard_settings = AccountSettingsForm(request.POST)
        if standard_settings.is_valid():
            clean_data = standard_settings.cleaned_data
            for item in clean_data:
                if clean_data[item]:
                    # TODO do we need to hide the password in the POST and not
                    # just when we are storing it?
                    if(item == 'password1' or item == 'password2'):
                        if(clean_data['password1'] == clean_data['password2']):
                            user.set_password(clean_data[item])
                    else:
                        # According to PEP 363 this should be 
                        # user.('%s' % item) = clean_data[item] but when I
                        # attempt this django reports invalid syntax...
                        setattr(user, ('%s' % item), clean_data[item])
            user.save()
            return HttpResponseRedirect('/user_profiles/')
    else:
        standard_settings = AccountSettingsForm()
    return_dict = {
                    'standard_settings': standard_settings,
                  }
    return render_to_response('settings/standard_settings.html',
                              return_dict,
                              RequestContext(request))

@login_required
def address_settings(request):
    user = User.objects.get(username=request.user)
    if request.method == 'POST':
        address_settings = AddressSettingsForm(request.POST)
        if(address_settings.is_valid()):
            clean_data = address_settings.cleaned_data
            for item in clean_data:
                if clean_data[item]:
                    setattr(user, ('%s' % item), clean_data[item])
            user.save()
            return HttpResponseRedirect('/user_profiles/')
    else:
        address_settings = AddressSettingsForm()
    return_dict = {
                    'address_form': address_settings,
                  }
    return render_to_response('settings/address_settings.html',
                              return_dict,
                              RequestContext(request))

@login_required
def user_settings(request):
    user = User.objects.get(username=request.user)
    profile_util = ProfileUtils(user, user)
    if request.method == 'POST':
        settings_form = profile_util.get_settings_form_post(request.POST)
        if(settings_form.is_valid()):
            clean_data = settings_form.cleaned_data
            user_profile = profile_util.get_user_profile(user)
            for item in clean_data:
                if clean_data[item]:
                    setattr(user_profile, ('%s' % item), clean_data[item])
            user_profile.save()
            return HttpResponseRedirect('/user_profiles/')
    else:
        settings_form = profile_util.get_settings_form()
    
    return_dict = {
                    'settings_form': settings_form,
                  }
    return render_to_response('settings/user_settings.html',
                              return_dict,
                              RequestContext(request))

@login_required
def picture_settings(request):
    user = User.objects.get(username=request.user)
    profile_util = ProfileUtils(user, user)
    user_profile = profile_util.get_user_profile(user)
    if request.method == 'POST':
        '''
        request.POST['album'] = Album.objects.get(user=user, name='Profile Pictures').id
        picture_form = ImageForm(user, request.POST, request.FILES)
        if picture_form.is_valid():
            image_object = picture_form.save(commit=False)
            image_object.user = user
            image_object.save()
            if image_object.album:
                image_object.album.save()
                user_profile.profile_pic = image_object
                user_profile.save()
        '''
        return HttpResponseRedirect('/user_profiles/')
    else:
        #picture_form = ImageForm(user)
        pass
    
    return_dict = {
                    'profile_pic': user_profile.profile_pic,
                  }
    return render_to_response('settings/picture_settings.html',
                              return_dict,
                              RequestContext(request))


def search(request):
    if request.method == 'POST':
        print request.method
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_view = SearchView()
            search_view.form = search_form
            search_view.request = request
            search_view.results = search_form.search()
            paginator, page = search_view.build_page()
            return_dict = {
                            'form': search_form,
                            'query': search_view.get_query(),
                            'page': page,
                            'paginator': paginator,
                            'suggestion': None,
                          }
            return render_to_response('search/search.html', return_dict,
                                      RequestContext(request))
    search_form = SearchForm()
    return_dict = {
                    'form': search_form,
                  }
                  
    return render_to_response('search/search.html',
                                return_dict,
                                RequestContext(request))
