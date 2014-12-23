from django import forms

class PolicyForm(forms.Form):
    policies = forms.CharField(max_length=150)
    description = forms.CharField(widget=forms.Textarea)

class AgendaForm(forms.Form):
    agenda = forms.CharField(widget=forms.Textarea)

class ResumeForm(forms.Form):
    title = forms.CharField()
    start_date = forms.DateField()
    end_date = forms.DateField()
    current = forms.BooleanField()
    company = forms.CharField()
    location = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

class GoalForm(forms.Form):
    pass