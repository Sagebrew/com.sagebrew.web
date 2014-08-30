from django import forms

class SaveQuestionForm(forms.Form):
    question_title = forms.CharField()
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

class GetQuestionForm(forms.Form):
    sort_by = forms.CharField()
    user = forms.EmailField()
    current_pleb = forms.EmailField()
    question_uuid = forms.CharField()

class VoteQuestionForm(forms.Form):
    question_uuid = forms.CharField()
    current_pleb = forms.EmailField()
    vote_type = forms.CharField()
