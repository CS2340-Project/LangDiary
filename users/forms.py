from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from .models import Profile
from .models import UserPreferences

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ResetPasswordForm(PasswordResetForm):
    pass

class CustomSetPasswordForm(SetPasswordForm):
    pass

class UserPreferencesForm(forms.ModelForm):
    COMMITMENT_CHOICES = [
        ('casual', 'Casual (5-10 minutes)'),
        ('regular', 'Regular (15-20 minutes)'),
        ('dedicated', 'Dedicated (30+ minutes)'),
        ('intense', 'Intense (60+ minutes)'),
    ]

    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner (A1)'),
        ('elementary', 'Elementary (A2)'),
        ('intermediate', 'Intermediate (B1)'),
        ('upper_intermediate', 'Upper Intermediate (B2)'),
        ('advanced', 'Advanced (C1)'),
        ('proficient', 'Proficient (C2)'),
    ]

    commitment_level = forms.ChoiceField(choices=COMMITMENT_CHOICES, required=True)
    skill_level = forms.ChoiceField(choices=SKILL_LEVEL_CHOICES, required=True)

    goals = forms.MultipleChoiceField(
        choices=[
            ('conversation', 'Daily conversation'),
            ('travel', 'Travel'),
            ('work', 'Work/Professional'),
            ('academic', 'Academic/School'),
            ('exam', 'Exam preparation'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    areas = forms.MultipleChoiceField(
        choices=[
            ('speaking', 'Speaking'),
            ('listening', 'Listening'),
            ('reading', 'Reading'),
            ('writing', 'Writing'),
            ('grammar', 'Grammar'),
            ('vocabulary', 'Vocabulary'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = UserPreferences
        fields = ['commitment_level', 'skill_level', 'goals', 'areas']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')

        if instance and instance.pk:
            # Convert comma-separated string to list for initial form data
            initial = kwargs.get('initial', {})
            initial['goals'] = instance.get_goals_list()
            initial['areas'] = instance.get_areas_list()
            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Convert list to comma-separated string
        instance.set_goals_list(self.cleaned_data['goals'])
        instance.set_areas_list(self.cleaned_data['areas'])

        if commit:
            instance.save()

        return instance

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