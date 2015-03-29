from django import forms


class SavePostForm(forms.Form):
    content = forms.CharField()
    current_user = forms.CharField()
    page_user = forms.CharField()


class GetPostForm(forms.Form):
    page_user = forms.CharField()
    range_end = forms.IntegerField()
    range_start = forms.IntegerField()
