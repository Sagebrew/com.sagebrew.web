from django import forms


class SubmitFriendRequestForm(forms.Form):
    from_user = forms.CharField()
    to_user = forms.CharField()


class GetFriendRequestForm(forms.Form):
    email = forms.EmailField()


class RespondFriendRequestForm(forms.Form):
    request_id = forms.CharField()
    response = forms.CharField()

