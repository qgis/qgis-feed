from django.contrib.gis import forms
from django.forms import ValidationError

from .models import CharacterLimitConfiguration, QgisFeedEntry
from .languages import LANGUAGES
from django.utils import timezone

class HomePageFilterForm(forms.Form):
    """
    Form for feed entry filter on the home page
    """
    empty_lang = ('', 'Select a language')
    LANG_CHOICES = (empty_lang,) + LANGUAGES

    lang = forms.ChoiceField(
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


class FeedEntryFilterForm(forms.Form):
    """
    Form for feed entry filter on the feed list
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

    need_review = forms.ChoiceField(
        required=False,
        widget=forms.Select(),
        choices=[('', 'Select an option'), (1, 'Yes'), (0, 'No')]
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

    def __init__(self, *args, **kwargs):
        super(FeedItemForm, self).__init__(*args, **kwargs)
        # Custom fields widget
        self.fields['title'].widget = forms.TextInput(attrs={'class': 'input', 'placeholder': 'Title', 'maxlength': self.fields['title'].max_length})
        self.fields['image'].widget = forms.FileInput(attrs={'class': 'file-input'})
        self.fields['content'].widget = forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Content', 'rows': 5})
        self.fields['url'].widget = forms.TextInput(attrs={'class': 'input', 'placeholder': 'URL for more information link'})
        self.fields['sorting'].widget = forms.NumberInput(attrs={'class': 'input',  'placeholder': 'Increase to show at top of the list'})
        self.fields['spatial_filter'].widget = forms.OSMWidget(attrs={
            'geom_type': 'Polygon',
            'map_width': '100%', 
            'map_height': 500,
            'default_lat': 0,
            'default_lon': 0,
            'default_zoom': 2
        })
        self.fields['publish_from'].widget = forms.DateTimeInput(
            attrs={
                'type': 'datetime-local', 
                'class': 'input', 
                }
        )
        self.fields['publish_from'].initial = timezone.now()

        self.fields['publish_to'].widget = forms.DateTimeInput(
            attrs={
                'type': 'datetime-local', 
                'class': 'input', 
                }
        )
        self.fields['publish_to'].initial = timezone.now() + timezone.timedelta(days=30)

    def clean_content(self):
        content = self.cleaned_data['content']
        try:
            config = CharacterLimitConfiguration.objects.get(field_name="content")
            content_max_length = config.max_characters
        except CharacterLimitConfiguration.DoesNotExist:
            content_max_length = 500
        
        if len(content) > content_max_length:
            raise ValidationError(
                f"Ensure this value has at most {str(content_max_length)} characters (it has {str(len(content))})."
            )
        return content


    sticky = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )
