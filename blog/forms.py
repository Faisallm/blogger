from django import forms


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