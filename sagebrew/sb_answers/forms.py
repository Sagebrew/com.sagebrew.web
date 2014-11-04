from django import forms


class SaveAnswerForm(forms.Form):
    question_uuid = forms.CharField()
    current_pleb = forms.EmailField()
    content = forms.CharField()

class EditAnswerForm(forms.Form):
    answer_uuid = forms.CharField()
    current_pleb = forms.EmailField()
    content = forms.CharField()
    last_edited_on = forms.DateTimeField()


class GetAnswerForm(forms.Form):
    range_end = forms.IntegerField()
    range_start = forms.IntegerField()