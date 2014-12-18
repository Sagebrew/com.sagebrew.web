from django import forms

class UpdateNeoForm(forms.Form):
    current_pleb = forms.CharField()