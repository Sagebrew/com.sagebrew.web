from django import forms
from django.conf import settings

class CommentForm(forms.Form):
    current_pleb = forms.EmailField(required=True)

class SaveCommentForm(CommentForm):
    content = forms.CharField(min_length=10)
    object_uuid = forms.CharField()
    object_type = forms.ChoiceField(choices=settings.KNOWN_TYPES)


