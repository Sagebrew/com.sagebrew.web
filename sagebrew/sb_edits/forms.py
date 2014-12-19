from django import forms


class EditObjectForm(forms.Form):
    content = forms.CharField(min_length=15)
    object_type = forms.CharField()
    object_uuid = forms.CharField()
    datetime = forms.CharField(initial=None, required=False)
    parent_object = forms.CharField(initial=None, required=False)

class EditQuestionForm(forms.Form):
    question_title = forms.CharField(min_length=6)
    object_type = forms.CharField()
    object_uuid = forms.CharField()
