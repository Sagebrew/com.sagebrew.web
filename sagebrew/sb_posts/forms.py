from django import forms


class PostForm(forms.Form):
    content = forms.CharField()
    current_pleb = forms.EmailField()


class SavePostForm(PostForm):
    wall_pleb = forms.EmailField()


class GetPostForm(forms.Form):
    current_user = forms.EmailField()
    email = forms.EmailField()
    range_end = forms.IntegerField()
    range_start = forms.IntegerField()
