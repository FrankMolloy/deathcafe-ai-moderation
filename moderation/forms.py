from django import forms
from .models import Post


class PostSubmissionForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "image"]