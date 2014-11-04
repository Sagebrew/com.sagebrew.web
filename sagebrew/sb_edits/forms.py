from django import forms


class EditObjectForm(forms.Form):
    content = forms.CharField(min_length=15)
    question_title = forms.CharField(min_length=5, required=False)
    current_pleb = forms.EmailField()
    object_type = forms.CharField()
    object_uuid = forms.CharField()
