from django import forms

class PostForm(forms.Form):
    content = forms.CharField()
    current_pleb = forms.EmailField()

class SavePostForm(PostForm):
    wall_pleb = forms.EmailField()

class EditPostForm(PostForm):
    post_uuid = forms.CharField()
    last_edited_on = forms.DateTimeField()
