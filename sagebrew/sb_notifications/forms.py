from django import forms

class GetNotificationForm(forms.Form):
    range_start = forms.IntegerField()
    range_end = forms.IntegerField()