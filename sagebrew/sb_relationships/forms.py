from django import forms

class SubmitFriendRequestForm(forms.Form):
    from_pleb = forms.CharField()
    to_pleb = forms.CharField()
    friend_request_uuid = forms.CharField()

