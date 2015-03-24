from django import forms


class SaveQuestionForm(forms.Form):
    title = forms.CharField()
    current_pleb = forms.CharField()
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
        ('uuid', 'uuid'),
        ('recent_edit', 'recent_edit')
    )
    sort_by = forms.ChoiceField(choices=choices)
    question_uuid = forms.CharField(required=False)
