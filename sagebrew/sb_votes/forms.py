from django import forms


known_types = [
    ("SBPost", "SBPost"), ("SBAnswer", "SBAnswer"),
    ("SBQuestion", "SBQuestion"), ("SBComment", "SBComment")
]

class VoteObjectForm(forms.Form):
    object_uuid = forms.CharField()
    object_type = forms.MultipleChoiceField(choices=known_types, required=True)
    vote_type = forms.CharField()
    current_pleb = forms.CharField()