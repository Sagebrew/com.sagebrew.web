from django import forms


class SearchForm(forms.Form):
    display_num = forms.IntegerField()
    query_param = forms.CharField()
    page = forms.IntegerField()
