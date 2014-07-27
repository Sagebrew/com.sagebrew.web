from django import forms

class CommentForm(forms.Form):
    pleb = forms.EmailField(
        required=True
    )

class SaveCommentForm(CommentForm):
    content = forms.CharField()
    post_uuid = forms.CharField()

class EditCommentForm(CommentForm):
    content = forms.CharField()
    last_edited_on = forms.DateTimeField()
    comment_uuid = forms.CharField()
