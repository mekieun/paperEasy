from django import forms
from .models import Bookmark


class BookmarkCreateForm(forms.ModelForm):
    class Meta:
        model = Bookmark
        fields = ('site_name', 'url', 'author')

        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-class', 'value': '', 'id': 'who', 'type': 'hidden'}),
        }
