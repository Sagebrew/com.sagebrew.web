from django import forms

class GetUserSearchForm(forms.Form):
    email = forms.EmailField()