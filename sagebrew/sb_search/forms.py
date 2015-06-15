from django import forms
from django.conf import settings


class SearchForm(forms.Form):
    display_num = forms.IntegerField()
    query_param = forms.CharField()
    page = forms.IntegerField()
