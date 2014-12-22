from django import forms

class PolicyForm(forms.Form):
    policies = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)

class AgendaForm(forms.Form):
    agenda = forms.CharField(widget=forms.Textarea)

class ResumeForm(forms.Form):
    resume = forms.CharField(widget=forms.Textarea)

class GoalForm(forms.Form):
    pass