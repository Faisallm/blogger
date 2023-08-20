from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    # name of the person sending the email
    name = forms.CharField(max_length=25)
    # sender's email
    email = forms.EmailField()
    # receiver's email
    to = forms.EmailField()
    # sender's comments, optional
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)
    

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    # form input for the search query
    query = forms.CharField()