from django import forms


class EditObjectForm(forms.Form):
    content = forms.CharField()
    object_type = forms.CharField()
    object_uuid = forms.CharField()
    created = forms.CharField(initial=None, required=False)
    parent_object = forms.CharField(initial=None, required=False)


class EditQuestionForm(forms.Form):
    title = forms.CharField(min_length=6)
    object_type = forms.CharField()
    object_uuid = forms.CharField()
