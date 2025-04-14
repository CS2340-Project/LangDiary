# flashcards/forms.py
from django import forms

class FlashcardGeneratorForm(forms.Form):
    LANGUAGE_CHOICES = [
        ('spanish', 'Spanish'),
        ('french', 'French'),
        ('german', 'German'),
    ]
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    TOPIC_CHOICES = [
        ('greetings', 'Greetings & Introductions'),
        ('food', 'Food & Dining'),
        ('travel', 'Travel & Directions'),
        ('shopping', 'Shopping'),
        ('business', 'Business & Work'),
        ('hobbies', 'Hobbies & Free Time'),
        ('family', 'Family & Relationships'),
        ('health', 'Health & Medical'),
        ('home', 'Home & Housing'),
        ('culture', 'Culture & Customs'),
        ('education', 'Education & Learning'),
        ('technology', 'Technology & Internet'),
        ('environment', 'Environment & Nature'),
        ('custom', 'Custom Topic'),
    ]
    
    COUNT_CHOICES = [
        (5, '5'),
        (10, '10'),
        (15, '15'),
        (20, '20'),
    ]
    
    language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full p-3 border border-slate-600 rounded-lg focus:ring-2 focus:ring-red-400 focus:border-transparent bg-slate-700 text-white shadow-inner transition-all'})
    )
    
    level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full p-3 border border-slate-600 rounded-lg focus:ring-2 focus:ring-red-400 focus:border-transparent bg-slate-700 text-white shadow-inner transition-all'})
    )
    
    topic = forms.ChoiceField(
        choices=TOPIC_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full p-3 border border-slate-600 rounded-lg focus:ring-2 focus:ring-red-400 focus:border-transparent bg-slate-700 text-white shadow-inner transition-all'})
    )
    
    custom_topic = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-3 border border-slate-600 rounded-lg focus:ring-2 focus:ring-red-400 focus:border-transparent bg-slate-700 text-white shadow-inner transition-all',
            'placeholder': 'Enter custom topic'
        })
    )
    
    count = forms.ChoiceField(
        choices=COUNT_CHOICES,
        initial=5,
        widget=forms.Select(attrs={'class': 'w-full p-3 border border-slate-600 rounded-lg focus:ring-2 focus:ring-red-400 focus:border-transparent bg-slate-700 text-white shadow-inner transition-all'})
    )