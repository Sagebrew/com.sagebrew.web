from django import forms


class EditObjectForm(forms.Form):
    content = forms.CharField(min_length=15)
    current_pleb = forms.EmailField()
    object_type = forms.CharField()
    object_uuid = forms.CharField()
    parent_object = forms.CharField(initial=None, required=False)

class EditQuestionForm(forms.Form):
    question_title = forms.CharField(min_length=6)
    current_pleb = forms.EmailField()
    object_type = forms.CharField()
    object_uuid = forms.CharField()
