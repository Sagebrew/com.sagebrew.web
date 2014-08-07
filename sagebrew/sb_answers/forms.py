from django import forms

class SaveAnswerForm(forms.Form):
    question_uuid = forms.CharField()
    current_pleb = forms.EmailField()
    content = forms.CharField()
    to_pleb = forms.EmailField()

class EditAnswerForm(forms.Form):
    answer_uuid = forms.CharField()
    current_pleb = forms.EmailField()
    content = forms.CharField()
    last_edited_on = forms.DateTimeField()

class VoteAnswerForm(forms.Form):
    answer_uuid = forms.CharField()
    current_pleb = forms.EmailField()
    vote_type = forms.CharField()

class GetAnswerForm(forms.Form):
    range_end = forms.IntegerField()
    range_start = forms.IntegerField()