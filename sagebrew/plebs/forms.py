from django import forms


class SubmitFriendRequestForm(forms.Form):
    to_username = forms.CharField()


class GetFriendRequestForm(forms.Form):
    email = forms.EmailField()