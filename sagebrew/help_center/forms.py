from django import forms


class RelatedArticlesForm(forms.Form):
    current_article = forms.CharField(max_length=128)
    category = forms.CharField(max_length=128, required=False)
