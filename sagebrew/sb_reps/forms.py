from django import forms

class PolicyForm(forms.Form):
    policies = forms.CharField(max_length=150)
    description = forms.CharField(widget=forms.Textarea)

class AgendaForm(forms.Form):
    agenda = forms.CharField(widget=forms.Textarea)

class ExperienceForm(forms.Form):
    title = forms.CharField()
    start_date = forms.DateField()
    end_date = forms.DateField()
    current = forms.BooleanField(required=False)
    company = forms.CharField()
    location = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

class GoalForm(forms.Form):
    vote_req = forms.IntegerField()
    money_req = forms.FloatField()
    description = forms.CharField()

class DonationForm(forms.Form):
    cost = forms.FloatField()
    description = forms.CharField()

class EducationForm(forms.Form):
    school = forms.CharField()
    start_date = forms.DateField()
    end_date = forms.DateField()
    degree = forms.CharField()
