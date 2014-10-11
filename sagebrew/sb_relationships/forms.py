from django import forms

class SubmitFriendRequestForm(forms.Form):
    from_pleb = forms.CharField()
    to_pleb = forms.CharField()
    friend_request_uuid = forms.CharField()

class GetFriendRequestForm(forms.Form):
    email = forms.EmailField()

class RespondFriendRequestForm(forms.Form):
    request_id = forms.CharField()
    response = forms.CharField()

