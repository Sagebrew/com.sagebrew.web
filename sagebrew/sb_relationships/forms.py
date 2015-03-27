from django import forms


class SubmitFriendRequestForm(forms.Form):
    from_username = forms.CharField()
    to_username = forms.CharField()


class GetFriendRequestForm(forms.Form):
    email = forms.EmailField()


class RespondFriendRequestForm(forms.Form):
    request_id = forms.CharField()
    response = forms.CharField()

