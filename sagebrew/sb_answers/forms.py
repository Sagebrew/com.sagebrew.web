from django import forms


class SaveAnswerForm(forms.Form):
    question_uuid = forms.CharField()
    current_pleb = forms.EmailField()
    content = forms.CharField()

class GetAnswerForm(forms.Form):
    range_end = forms.IntegerField()
    range_start = forms.IntegerField()