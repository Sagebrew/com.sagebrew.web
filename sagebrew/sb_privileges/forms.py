from django import forms
from django.conf import settings

class CreatePrivilegeForm(forms.Form):
    name = forms.CharField()


class CreateActionForm(forms.Form):
    action = forms.CharField()
    object_type = forms.ChoiceField(choices=settings.KNOWN_TYPES)
    url = forms.CharField()
    html_object = forms.CharField(required=False)


class CreateRequirementForm(forms.Form):
    url = forms.CharField()
    name = forms.CharField()
    key = forms.CharField()
    operator = forms.ChoiceField(choices=settings.OPERATOR_TYPES)
    condition = forms.CharField()
    auth_type = forms.CharField(required=False)


class SelectActionForm(forms.Form):
    object_uuid = forms.CharField()


class SelectRequirementForm(forms.Form):
    object_uuid = forms.CharField()


class CreateRestrictionForm(forms.Form):
    pass


class CheckActionForm(forms.Form):
    action = forms.CharField()