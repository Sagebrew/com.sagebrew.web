from django import forms
from django.conf import settings


class SaveCommentForm(forms.Form):
    content = forms.CharField(min_length=10)
    object_uuid = forms.CharField()
    object_type = forms.ChoiceField(choices=settings.KNOWN_TYPES)


