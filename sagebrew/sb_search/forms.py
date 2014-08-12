from django import forms

class SearchForm(forms.Form):
    query_param = forms.CharField()