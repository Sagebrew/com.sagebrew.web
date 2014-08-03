from django import forms

class SaveQuestionForm(forms.Form):
    current_pleb = forms.EmailField()
    content = forms.CharField()

class EditQuestionForm(forms.Form):
    question_uuid = forms.CharField()
    current_pleb = forms.EmailField()
    content = forms.CharField()
    last_edited_on = forms.DateTimeField()

class DeleteQuestionForm(forms.Form):
    current_pleb = forms.EmailField()
    question_uuid = forms.CharField()

class CloseQuestionForm(forms.Form):
    current_pleb = forms.EmailField()
    question_uuid = forms.CharField()
    reason = forms.CharField()