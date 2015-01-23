from django import forms


class CreateBadgeForm(forms.Form):
    badge_name = forms.CharField()
    badge_group_id = forms.CharField()
    badge_group_name = forms.CharField()
    badge_level = forms.CharField()
    # sage_badge = forms.BooleanField() #This is something that only certain people will have the ability to do