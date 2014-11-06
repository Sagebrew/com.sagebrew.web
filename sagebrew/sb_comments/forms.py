from django import forms


class CommentForm(forms.Form):
    pleb = forms.EmailField(required=True)


class SaveCommentForm(CommentForm):
    content = forms.CharField()
    post_uuid = forms.CharField()


class DeleteCommentForm(CommentForm):
    comment_uuid = forms.CharField()


