from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class InterestForm(forms.Form):
    select_all = forms.BooleanField(
        label = "I like a bit of everything",
        required = False,
        help_text='I really like to talk a lot'
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


    def __init__(self, *args, **kwargs):
        super(InterestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'

        self.helper.add_input(Submit('submit', 'Submit'))