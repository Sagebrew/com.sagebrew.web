from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm
from django.utils.translation import ugettext_lazy as _

from localflavor.us.forms import USZipCodeField, USStateField


class InterestForm(forms.Form):
    select_all = forms.BooleanField(
        label="I like a bit of everything",
        required=False,
    )

    fiscal = forms.BooleanField(
        label="Fiscal",
        required=False,
        help_text='''
            Issues involving the Economy,
            matters of taxation, government spending,
            importing/exporting, the private sector,
            wall street etc
        '''
    )

    foreign_policy = forms.BooleanField(
        label="Foreign Policy",
        required=False,
        help_text='''
            Issues involving the interaction between the Federal Government
            and Governments of other states and nations.
        '''
    )

    social = forms.BooleanField(
        label="Social",
        required=False,
        help_text='''
            Issues that effect the advancement of society:
            Abortion, LGBT rights, social injustice, Gun Control, personal
            freedoms etc
        '''
    )

    education = forms.BooleanField(
        label="Education",
        required=False,
        help_text='''
            Issues involving the education of the nation's including
            educational reform, policy changes, curriculum changes, the arts
            etc.
        '''
    )

    science = forms.BooleanField(
        label="Science",
        required=False,
        help_text='''
            Issues rooted in science such as: climate change, stem cell
            research, product testing, genetic engineering etc.
        '''
    )

    environment = forms.BooleanField(
        label="Environment",
        required=False,
        help_text='''
            Issues that deal with the national and global climate such as:
            carbon pollution, other forms of chemical air pollution,
            water pollution, sewage dumping, plastics and recycling, trash
            and cleanup etc.
        '''
    )

    drugs = forms.BooleanField(
        label="Drugs",
        required=False,
        help_text='''
            Issues that deal with prescription drugs,
            recreational drugs, drug laws, drug penalties,
            drug psychology, etc.
        '''
    )

    agriculture = forms.BooleanField(
        label="Agriculture",
        required=False,
        help_text='''
            Issues that look at agricultural law, practice, patent law,
            mono-cropping, agricultural reform etc.
        '''
    )

    defense = forms.BooleanField(
        label="Defense",
        required=False,
        help_text='''
            Issues involving the United States Defense program, such as:
            defense spending, defense spending allocation, weapons research,
            military, military benefits and healthcare, veteran affairs,
            wartime strategy and treaty etc.
        '''
    )

    energy = forms.BooleanField(
        label="Energy",
        required=False,
        help_text='''
            Issues involving alternative energy research, energy emissions
            control, current energy goals and practice, etc.
        '''
    )

    health = forms.BooleanField(
        label="Health",
        required=False,
        help_text='''
            Issues involving general healthcare, the ACA, insurance,
            health research, the FDA, etc.
        '''
    )

    space = forms.BooleanField(
        label="Space",
        required=False,
        help_text='''
            Issues that deal with the science of space travel,
            space exploration, astrophysics, astronomy, asteroid mining, etc.
        '''
    )

    specific_interests = forms.MultipleChoiceField(
        label="I only care about:",
        choices=[],
        required=False,
    )


class AddressInfoForm(forms.Form):
    primary_address = forms.CharField(
        label="Address Line 1",
        max_length=200,
        required=True,
    )

    street_additional = forms.CharField(
        label="Apt,Building,Etc",
        max_length=200,
        required=False,
    )

    city = forms.CharField(
        label="City",
        max_length=100,
        required=True,
    )

    state = USStateField()

    postal_code = USZipCodeField(
        label="Zip Code",
        max_length=10,
        required=True,
    )

    valid = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.HiddenInput()
    )

    original_selected = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput()
    )

    congressional_district = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

    latitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput()
    )

    longitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput()
    )

    county = forms.CharField(
        label="County",
        max_length=125,
        required=True,
    )


class ProfilePictureForm(forms.Form):
    picture = forms.FileField(
        label="Profile Picture"
    )
    image_x1 = forms.FloatField()
    image_x2 = forms.FloatField()
    image_y1 = forms.FloatField()
    image_y2 = forms.FloatField()


class ProfilePageForm(forms.Form):
    picture = forms.URLField(
        label='Profile Picture',
    )


class SignupForm(forms.Form):
    first_name = forms.CharField(required=True, max_length=30,
                                 label="First Name")
    last_name = forms.CharField(required=True, max_length=30,
                                label="Last Name")
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(required=True, min_length=6, max_length=56)
    password2 = forms.CharField(required=True, min_length=6, max_length=56)
    birthday = forms.DateTimeField(required=True, input_formats=['%m/%d/%Y'])


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=6)


def validate_user(email):
    try:
        User.objects.get(email=email)
        return email
    except User.DoesNotExist:
        raise ValidationError("There is no user associated with %s" % email)


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_("Email"), max_length=254,
                             validators=[validate_user])
