from django import forms
from .models import Exercise

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['content']
        widgets = {
            'writing': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Begin writing your response here...'})
        }
