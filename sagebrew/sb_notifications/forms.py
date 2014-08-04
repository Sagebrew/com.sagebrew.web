from django import forms

class GetNotificationForm(forms.Form):
    email = forms.EmailField()
    range_start = forms.IntegerField()
    range_end = forms.IntegerField()