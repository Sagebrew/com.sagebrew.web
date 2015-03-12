from django import forms

class GetUserSearchForm(forms.Form):
    username = forms.CharField()