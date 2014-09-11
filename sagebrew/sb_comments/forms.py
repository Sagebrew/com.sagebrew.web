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
    comment_uuid = forms.CharField()
    last_edited_on = forms.DateTimeField()


class DeleteCommentForm(CommentForm):
    comment_uuid = forms.CharField()


class VoteCommentForm(CommentForm):
    vote_type = forms.CharField()
    comment_uuid = forms.CharField()

class FlagCommentForm(forms.Form):
    current_user = forms.CharField()
    flag_reason = forms.CharField()
    comment_uuid = forms.CharField()
