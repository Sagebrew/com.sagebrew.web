from django import forms

class SaveQuestionForm(forms.Form):
    question_title = forms.CharField()
    current_pleb = forms.EmailField()
    content = forms.CharField()
    tags = forms.CharField()

class DeleteQuestionForm(forms.Form):
    current_pleb = forms.EmailField()
    question_uuid = forms.CharField()

class CloseQuestionForm(forms.Form):
    current_pleb = forms.EmailField()
    question_uuid = forms.CharField()
    reason = forms.CharField()

class GetQuestionForm(forms.Form):
    choices = (
        ('most_recent', 'most_recent'),
        ('least_recent', 'least_recent'),
        ('uuid', 'uuid')
    )
    sort_by = forms.ChoiceField()
    user = forms.EmailField()
    current_pleb = forms.EmailField()
    question_uuid = forms.CharField()
