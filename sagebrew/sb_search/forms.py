from django import forms

class SearchForm(forms.Form):
    display_num = forms.IntegerField()
    range_start = forms.IntegerField()
    range_end = forms.IntegerField()
    query_param = forms.CharField()
    page = forms.IntegerField()

class SearchFormApi(forms.Form):
    query_param = forms.CharField()
    page = forms.IntegerField()
    display_num = forms.IntegerField()
    filter_type = forms.CharField(required=False)
    filter_param = forms.CharField(required=False)