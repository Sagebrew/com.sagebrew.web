from django import forms


class PostForm(forms.Form):
    content = forms.CharField()
    current_pleb = forms.EmailField()


class SavePostForm(PostForm):
    wall_pleb = forms.EmailField()


class EditPostForm(PostForm):
    post_uuid = forms.CharField()
    last_edited_on = forms.DateTimeField()


class DeletePostForm(forms.Form):
    pleb = forms.CharField()
    post_uuid = forms.CharField()


class VotePostForm(forms.Form):
    pleb = forms.CharField()
    post_uuid = forms.CharField()
    vote_type = forms.CharField()