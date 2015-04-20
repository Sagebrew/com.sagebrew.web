from django import forms
from django.conf import settings


class SearchForm(forms.Form):
    display_num = forms.IntegerField()
    query_param = forms.CharField()
    page = forms.IntegerField()


class SearchFormApi(forms.Form):
    query_param = forms.CharField()
    page = forms.IntegerField()
    display_num = forms.IntegerField()
    filter_param = forms.ChoiceField(choices=settings.SEARCH_TYPES,
                                     required=False)
