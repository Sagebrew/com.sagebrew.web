from django import forms


class SaveSolutionForm(forms.Form):
    question_uuid = forms.CharField()
    current_pleb = forms.CharField()
    content = forms.CharField()

class GetSolutionForm(forms.Form):
    range_end = forms.IntegerField()
    range_start = forms.IntegerField()