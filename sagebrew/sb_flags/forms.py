from django import forms

class FlagObjectForm(forms.Form):
    object_uuid = forms.CharField()
    object_type = forms.CharField()
    flag_reason = forms.CharField()
