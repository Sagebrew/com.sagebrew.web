from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class InterestForm(forms.Form):
    select_all = forms.BooleanField(
        label = "I like a bit of everything",
        required = False,
    )

    fiscal = forms.BooleanField(
        label = "Fiscal",
        required = False,
    )

    foreign_policy = forms.BooleanField(
        label = "Foreign Policy",
        required = False,
    )

    social = forms.BooleanField(
        label = "Social",
        required = False,
    )

    education = forms.BooleanField(
        label = "Education",
        required = False,
    )

    science = forms.BooleanField(
        label = "Science",
        required = False,
    )

    environment = forms.BooleanField(
        label = "Environment",
        required = False,
    )

    drugs = forms.BooleanField(
        label = "Drugs",
        required = False,
    )

    agriculture = forms.BooleanField(
        label = "Agriculture",
        required = False,
    )

    defense = forms.BooleanField(
        label = "Defense",
        required = False,
    )

    energy = forms.BooleanField(
        label = "Energy",
        required = False,
    )

    health = forms.BooleanField(
        label = "Health",
        required = False,
    )

    space = forms.BooleanField(
        label = "Space",
        required = False,
    )

    specific_interests = forms.MultipleChoiceField(
        label = "I only care about:",
        choices = [("HI", "Hawaii"), ("Bye", "Goodbye")],
        required = False,
    )


    def __init__(self, *args, **kwargs):
        super(InterestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'

        self.helper.add_input(Submit('submit', 'Submit'))

class ProfileInfoForm(forms.Form):
    '''first_name = forms.CharField(
        label = "First Name*",
        max_length = 40,
        required = True,
    )

    last_name = forms.CharField(
        label = "Last Name*",
        max_length = 40,
        required = True,
    )

    age = forms.IntegerField(
        label = "Age*",
        required = True,
    )'''

    '''email = forms.EmailField(
        label = "email*",
        required = True,
    )'''

    date_of_birth = forms.DateTimeField(
        label = "Birthday*",
        required = True,
    )

    '''primary_phone = forms.CharField(
        label = "Primary Phone",
        max_length = 11,
        required = False,
    )

    secondary_phone = forms.CharField(
        label = "Secondary Phone",
        max_length = 11,
        required = False,
    )

    profile_pic = forms.URLField(
        label = "Profile Picture",
        required = False,
    )'''

    home_town = forms.CharField(
        label = "Hometown",
        max_length = 40,
        required = False,
    )

    high_school = forms.CharField(
        label = "High School",
        max_length= 50,
        required = False,
    )

    college = forms.CharField(
        label = "College/University",
        max_length = 50,
        required = False,
    )

    employer = forms.CharField(
        label = "Employer",
        max_length = 50,
        required = False,
    )
class AddressInfo(forms.Form):
    primary_address = forms.CharField(
        label = "Primary Address*",
        max_length = 200,
        required = True,
    )

    address_additional = forms.CharField(
        label = "Apt,Building,Etc*",
        max_length = 200,
        required = True,
    )

    city = forms.CharField(
        label = "City*",
        max_length = 100,
        required = True,
    )

    state = forms.CharField(
        label = "State*",
        max_length = 25,
        required = True,
    )

    postal_code = forms.CharField(
        label = "Postal Code*",
        max_length = 10,
        required = True,
    )

    country = forms.CharField(
        label = "Country*",
        max_length = 40,
        required = True,
    )


