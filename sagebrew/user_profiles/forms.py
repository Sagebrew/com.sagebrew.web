'''
User Profiles Form file. This file is used to generate forms for registering
user profiles and forms for changing the settings of a user profile.
The current profiles that can be registered and modified by this forms
file are Company Profiles, Employee Profiles, and Customer Profiles which
can all be found in the Models.py file.
'''
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper

from localflavor.us.forms import USPhoneNumberField

from .models import Profile


attrs_dict = {'class': 'required'}
REQUIRED_ERRORS = {'password': _('Password must be entered'),
                   'first_name': _('First Name must be entered'),
                   'last_name': _('Last Name must be entered'),
                   'phone': _('Phone Number must be entered'),
                   'company': _('Company Name is required'),
                   'employer': _("You must enter an employer"),
                   'user_type': _("User Type is required"),
                  }

USER_EXISTS_ERROR = _("We are sorry a User with that username already exists, \
                     please choose another one")
USERNAME_INVALID_ERROR = _('This value must contain only letters, \
                           numbers and underscores.')
EMAIL_DUPLICATE_ERROR = _("We are sorry this email address is already in use. \
                          Please supply a different email address.")
PASSWORD_MISMATCH_ERROR = _("The two password fields didn't match.")
USER_TYPE_ATTRS = {'onchange': "Dajaxice.registration.pagination(\
                                Dajax.process, {'option': this.value})",
                   'size': '1'}


class StandardUserForm(forms.Form):
    '''
    User registration form containing the attributes found in all user profiles
    '''
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                    render_value=False),
                    error_messages={'required': REQUIRED_ERRORS['password']})
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                    render_value=False),
                    error_messages={'required': REQUIRED_ERRORS['password']})
    primary_phone = USPhoneNumberField(
                        error_messages={'required': REQUIRED_ERRORS['phone']})

    def clean_username(self):
        'Validate that the username is alphanumeric and is not already in use.'
        username = self.cleaned_data['username']
        try:
            User.objects.get(username__iexact=username)
            Profile.objects.get(lower_username__iexact=username.lower())
        except User.DoesNotExist:
            return username
        except Profile.DoesNotExist:
            return username
        raise forms.ValidationError(USER_EXISTS_ERROR)

    def clean_email(self):
        'Validate that the supplied email address is unique for the site.'
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email):
            raise forms.ValidationError(EMAIL_DUPLICATE_ERROR)
        return email

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        pass1, pass2 = ('password1', 'password2')

        if(pass1 in self.cleaned_data and pass2 in self.cleaned_data):
            if(self.cleaned_data[pass1] != self.cleaned_data[pass2]):
                raise forms.ValidationError(PASSWORD_MISMATCH_ERROR)
        return self.cleaned_data


class ProfileForm(forms.Form):
    '''
    Registration form for the customer profile containing customer
    specific attributes.
    '''
    username = forms.CharField(max_length=30,
                   widget=forms.TextInput(attrs=attrs_dict),
                   error_messages={'invalid': USERNAME_INVALID_ERROR})
    first_name = forms.CharField(max_length=30,
                    error_messages={'required': REQUIRED_ERRORS['first_name']})
    last_name = forms.CharField(max_length=30,
                    error_messages={'required': REQUIRED_ERRORS['last_name']})


class AccountSettingsForm(forms.Form):
    '''
    Settings form for standard account attributes found within each of the
    user profiles.
    '''
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                    render_value=False), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                    render_value=False), required=False)


class SettingsWorkandEducation(forms.Form):
    pass


class SettingsAboutYou(forms.Form):
    pass


class SettingsBasicInfo(forms.Form):
    '''
        Birthday
        Sex
        ...
    '''
    pass


class SettingsAddress(forms.Form):
    pass


class SettingsContactInfo(forms.Form):
    pass


class SettingsSecurity(forms.Form):
    '''
        Security Question
        Secure Browsing
        Login Notifications
        Login Approvals
        App Passwords
        Recognize Devices
        Active Sessions
    '''
    pass


class SettingsPayment(forms.Form):
    '''
        Subscriptions
        Purchase History
        Payment Methods
        Preferred Currency
    '''
    pass
