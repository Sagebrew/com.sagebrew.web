from django import forms
from django.conf import settings


class DeleteObjectForm(forms.Form):
    object_type = forms.ChoiceField(choices=settings.KNOWN_TYPES)
    object_uuid = forms.CharField()