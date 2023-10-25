from django.contrib.gis import forms

from .models import QgisFeedEntry
from .languages import LANGUAGES
from django.utils import timezone

class FeedEntryFilterForm(forms.Form):
    """
    Form for feed entry filter
    """
    empty_lang = ('', 'Select a language')
    LANG_CHOICES = (empty_lang,) + LANGUAGES
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Title'})
    )
    author = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Author'})
    )

    language_filter = forms.ChoiceField(
        choices=LANG_CHOICES,
        required=False, 
        widget=forms.Select()
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
    publish_to = forms.CharField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'class': 'input', 
                }
            )
    )


class FeedItemForm(forms.ModelForm):
    """
    Form for feed entry add or update
    """
    class Meta:
        model = QgisFeedEntry
        fields = [
            'title', 
            'image', 
            'content', 
            'url', 
            'sticky', 
            'sorting', 
            'language_filter', 
            'spatial_filter', 
            'publish_from', 
            'publish_to'
        ]

    empty_lang = ('', 'Select a language')
    LANG_CHOICES = (empty_lang,) + LANGUAGES

    title = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Title'})
    )
    image = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'file-input'})
    )

    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Content', 'rows': 5})
    )

    url = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'URL for more information link'})
    )

    sticky = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )

    sorting = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'input',  'placeholder': 'Increase to show at top of the list'})
    )

    language_filter = forms.ChoiceField(
        choices=LANG_CHOICES,
        required=False, 
        widget=forms.Select()
    )

    spatial_filter = forms.PolygonField(
        required=False, 
        widget=forms.OSMWidget(attrs={
            'map_width': '100%', 
            'map_height': 500})
    )

    publish_from = forms.CharField(
        required=False,
        initial=timezone.now(),
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local', 
                'class': 'input', 
                }
            )
    )
    publish_to = forms.CharField(
        required=False,
        initial=timezone.now() + timezone.timedelta(days=30),
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local', 
                'class': 'input', 
                }
            )
    )
