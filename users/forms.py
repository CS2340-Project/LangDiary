from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'native_language', 'language_learning', 
                 'language_level', 'learning_goals', 'pref_reading', 'pref_writing',
                 'pref_speaking', 'pref_listening']
        
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'native_language': forms.TextInput(attrs={'placeholder': 'Enter your native language'}),
            'learning_goals': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What are your language learning goals?'}),
        }