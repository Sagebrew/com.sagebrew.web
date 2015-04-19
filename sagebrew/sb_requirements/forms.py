from django import forms
from django.conf import settings


class RequirementForm(forms.Form):
    url = forms.CharField()
    key = forms.CharField()
    operator = forms.ChoiceField(choices=settings.OPERATOR_TYPES)
    condition = forms.CharField()
