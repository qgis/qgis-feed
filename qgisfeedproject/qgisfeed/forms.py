# forms.py
from django import forms

class FeedEntryFilterForm(forms.Form):
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Title'})
    )
    author = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Author'})
    )
    publish_from = forms.CharField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'input', 
                }
            )
    )
