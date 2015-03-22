from django import forms


class PostForm(forms.Form):
    content = forms.CharField()
    current_pleb = forms.CharField()


class SavePostForm(PostForm):
    wall_pleb = forms.CharField()


class GetPostForm(forms.Form):
    current_user = forms.EmailField()
    email = forms.EmailField()
    range_end = forms.IntegerField()
    range_start = forms.IntegerField()
