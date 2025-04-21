from django import forms
from .models import LanguageVideo

class VideoGeneratorForm(forms.Form):
    """Form for generating language learning videos based on preferences."""
    
    language = forms.ChoiceField(
        choices=LanguageVideo.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent'
        })
    )
    
    level = forms.ChoiceField(
        choices=LanguageVideo.LEVEL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent'
        })
    )
    
    # Adding these fields back but hidden with default values
    video_type = forms.ChoiceField(
        choices=LanguageVideo.VIDEO_TYPE_CHOICES,
        initial='lesson',
        required=False,
        widget=forms.HiddenInput()
    )
    
    duration = forms.ChoiceField(
        choices=LanguageVideo.DURATION_CHOICES,
        initial='medium',
        required=False,
        widget=forms.HiddenInput()
    )
    
    count = forms.ChoiceField(
        choices=[(str(i), str(i)) for i in range(1, 11)],
        initial='1',
        required=False,
        widget=forms.HiddenInput()
    )