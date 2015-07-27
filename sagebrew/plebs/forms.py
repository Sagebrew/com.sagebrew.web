from django import forms


class GetUserSearchForm(forms.Form):
    username = forms.CharField()


class SubmitFriendRequestForm(forms.Form):
    to_username = forms.CharField()


class GetFriendRequestForm(forms.Form):
    email = forms.EmailField()
