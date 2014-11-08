from django import forms


class CommentForm(forms.Form):
    current_pleb = forms.EmailField(required=True)


class SaveCommentForm(CommentForm):
    content = forms.CharField(min_length=10)
    object_uuid = forms.CharField()
    object_type = forms.CharField()

class DeleteCommentForm(CommentForm):
    comment_uuid = forms.CharField()


