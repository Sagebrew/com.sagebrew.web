'''
User Profiles Form file. This file is used to generate forms for registering
user profiles and forms for changing the settings of a user profile.
The current profiles that can be registered and modified by this forms
file are Company Profiles, Employee Profiles, and Customer Profiles which
can all be found in the Models.py file.
'''
from django import forms
from django.utils.translation import ugettext_lazy as _


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
