from django import forms
from django.conf import settings

class VoteObjectForm(forms.Form):
    object_uuid = forms.CharField()
    object_type = forms.ChoiceField(choices=settings.KNOWN_TYPES, required=True)
    vote_type = forms.BooleanField(required=False)
    current_pleb = forms.EmailField()