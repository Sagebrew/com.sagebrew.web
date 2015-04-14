from django import forms
from django.conf import settings


class VoteObjectForm(forms.Form):
    vote_type = forms.BooleanField(required=False)
    downvote_count = forms.IntegerField()