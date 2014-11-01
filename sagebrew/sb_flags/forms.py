from django import forms

known_type = (
    ("SBPost", "SBPost"), ("SBAnswer", "SBAnswer"),
    ("SBQuestion", "SBQuestion"), ("SBComment", "SBComment")
)
class FlagObjectForm(forms.Form):
    object_uuid = forms.CharField()
    object_type = forms.MultipleChoiceField(choices=known_type, required=True)
    flag_reason = forms.CharField()
    current_pleb = forms.CharField()
