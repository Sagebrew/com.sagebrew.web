from django import forms
from django.conf import settings


class FlagObjectForm(forms.Form):
    object_uuid = forms.CharField()
    object_type = forms.ChoiceField(choices=settings.KNOWN_TYPES, required=True)
    flag_reason = forms.CharField()
