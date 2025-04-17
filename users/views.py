from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from flashcards.profile_integration import get_user_language_preferences
from LangDiary import settings
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, PasswordResetForm, SetPasswordForm, \
    UserPreferencesForm
from .models import Goal, UserPreferences
import os 

from .models import Profile
from .forms import LanguageSelectionForm, ProficiencyLevelForm, LearningGoalsForm

def onboarding_language(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.language_learning:
            return redirect('users.profile')
    
    if request.method == 'POST':
        form = LanguageSelectionForm(request.POST)
        if form.is_valid():
            request.session['onboarding_language'] = form.cleaned_data['language']
            return redirect('users.onboarding_proficiency')
    else:
        initial_data = {}
        if 'onboarding_language' in request.session:
            initial_data = {'language': request.session['onboarding_language']}
        form = LanguageSelectionForm(initial=initial_data)
    
    return render(request, 'users/onboarding/language_selection.html', {'form': form, 'step': 1, 'total_steps': 3})

def onboarding_proficiency(request):
    if 'onboarding_language' not in request.session:
        return redirect('users.onboarding_language')
    
    if request.method == 'POST':
        form = ProficiencyLevelForm(request.POST)
        if form.is_valid():
            request.session['onboarding_proficiency'] = form.cleaned_data['level']
            return redirect('users.onboarding_goals')
    else:
        initial_data = {}
        if 'onboarding_proficiency' in request.session:
            initial_data = {'level': request.session['onboarding_proficiency']}
        form = ProficiencyLevelForm(initial=initial_data)
    
    selected_language = request.session['onboarding_language']
    language_display = dict(LanguageSelectionForm.LANGUAGE_CHOICES).get(selected_language, selected_language)
    
    return render(request, 'users/onboarding/proficiency_level.html', {
        'form': form, 
        'step': 2, 
        'total_steps': 3,
        'selected_language': selected_language,
        'language_display': language_display
    })

def onboarding_goals(request):
    # Check if language and proficiency are set in session
    if 'onboarding_language' not in request.session or 'onboarding_proficiency' not in request.session:
        return redirect('users.onboarding_language')
    
    if request.method == 'POST':
        form = LearningGoalsForm(request.POST)
        title = request.POST.get('goal_title')
        description = request.POST.get('goal_description')
        target_value_str = request.POST.get('goal_target')
        deadline = request.POST.get('goal_deadline')

        Goal.objects.create(
            user=request.user,
            title=title,
            description=description,
            target_value=int(target_value_str),
            current_value=0,  
            unit="flashcards",        
            deadline=deadline
        )
        profile = request.user.profile
        profile.language_learning = request.session['onboarding_language']
        profile.language_level = request.session['onboarding_proficiency']
        print(request.session['onboarding_language'])
        print(request.session['onboarding_proficiency'])
        print(profile.language_learning)
        profile.save()
        return redirect('users.onboarding_complete')
    return render(request, 'users/onboarding/learning_goals.html')

def onboarding_complete(request):
    profile = request.user.profile
    print(f"the profile is {profile}")
    print(f"but the language is {profile.language_learning}")
    
    
    return render(request, 'users/onboarding/onboarding_complete.html', {
        'profile': profile,
        'language_display': profile.language_learning,
        'level_display': profile.language_level,
    })

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Please complete your profile.')
            
            # Log the user in automatically after registration
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])
            login(request, user)
            
            # Redirect to profile page
            return redirect('users.onboarding_language')
    else:
        form = UserRegisterForm()
    
    context = {
        'form': form,
        'template_data': {
            'title': 'Register - LangDiary'
        }
    }
    return render(request, 'users/register.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('users.profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Get the user's goals
    user_goals = Goal.objects.filter(user=request.user)
    profile = request.user.profile
    profile_data = {'profile': profile,
        'language': profile.language_learning,
        "skill": profile.language_level}
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user_goals': user_goals,  # Add this to your context
        "profile_data": profile_data
    }
    return render(request, 'users/profile.html', context)


@login_required
def create_goal(request):
    if request.method == 'POST':
        title = request.POST.get('goal_title')
        description = request.POST.get('goal_description')
        target_value = int(request.POST.get('goal_target'))
        unit = request.POST.get('goal_unit')
        deadline = request.POST.get('goal_deadline') or None
        
        Goal.objects.create(
            user=request.user,
            title=title,
            description=description,
            target_value=target_value,
            current_value=0,  
            unit=unit,        
            deadline=deadline
        )
        
        messages.success(request, 'Goal created successfully!')
        return redirect('users.profile')
    
    return redirect('users.profile')

@login_required
def delete_profile_picture(request):
    """
    View to handle deleting the user's profile picture and replacing it with the default
    """
    if request.method == 'POST':
        profile = request.user.profile
        
        # Check if user has a custom profile picture (not the default)
        if profile.profile_picture and not profile.profile_picture.url.endswith('default.jpg'):
            # Get the file path
            if os.path.exists(profile.profile_picture.path):
                # Delete the physical file
                os.remove(profile.profile_picture.path)
            
            # Reset to default
            profile.profile_picture = 'profile_pics/default.jpg'
            profile.save()
            
            messages.success(request, 'Your profile picture has been removed.')
        else:
            messages.info(request, 'No custom profile picture to delete.')
            
    return redirect('users.profile')


@login_required
def edit_goal(request, goal_id):
    """View to handle editing an existing goal"""
    try:
        # Get the goal and verify it belongs to the current user
        goal = Goal.objects.get(id=goal_id, user=request.user)
    except Goal.DoesNotExist:
        messages.error(request, "Goal not found or you don't have permission to edit it.")
        return redirect('users.profile')
    
    if request.method == 'POST':
        # Update goal with form data
        goal.title = request.POST.get('goal_title')
        goal.description = request.POST.get('goal_description')
        goal.target_value = int(request.POST.get('goal_target'))
        goal.current_value = int(request.POST.get('goal_current', 0))
        goal.unit = request.POST.get('goal_unit')
        goal.deadline = request.POST.get('goal_deadline') or None
        
        goal.save()
        messages.success(request, 'Goal updated successfully!')
        return redirect('users.profile')
    
    # For GET requests, render the form
    return render(request, 'users/edit_goal.html', {'goal': goal})

@login_required
def delete_goal(request, goal_id):
    """View to handle deleting a goal"""
    try:
        # Get the goal and verify it belongs to the current user
        goal = Goal.objects.get(id=goal_id, user=request.user)
    except Goal.DoesNotExist:
        messages.error(request, "Goal not found or you don't have permission to delete it.")
        return redirect('users.profile')
    
    if request.method == 'POST':
        # Delete the goal
        goal.delete()
        messages.success(request, 'Goal deleted successfully!')
    
    return redirect('users.profile')

@login_required
def update_goal_progress(request, goal_id):
    """View to handle updating the progress of a goal"""
    try:
        goal = Goal.objects.get(id=goal_id, user=request.user)
    except Goal.DoesNotExist:
        messages.error(request, "Goal not found.")
        return redirect('users.profile')
    
    if request.method == 'POST':
        new_value = int(request.POST.get('current_value', 0))
        goal.current_value = new_value
        goal.save()
        messages.success(request, 'Progress updated!')
    
    return redirect('users.profile')


def reset_password_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=form.cleaned_data['email'])
                token = PasswordResetTokenGenerator().make_token(user=user)
                uid = urlsafe_base64_encode(str(user.id).encode())
                url = reverse('new_password', kwargs={'uid': uid, 'token': token})

                send_mail(
                    subject='Password Reset Request LangDiary',
                    message=f'Click the link below to reset your password http://127.0.0.1:8000{url}',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )


            except:
                pass
            return render(request, 'users/reset_password_request_done.html')

    else:
        form = PasswordResetForm()

    context = {
        'form': form,
        'template_data': {
            'title': 'Reset Password - LangDiary'
        }
    }
    return render(request, 'users/reset_password_request.html', context)


def new_password(request, uid, token):

    try:
        user = User.objects.get(id=urlsafe_base64_decode(uid))
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            raise Http404("Invalid or expired token.")

    except (User.DoesNotExist, ValueError, TypeError):
        raise Http404("Invalid or expired token.")

    if request.method == 'POST':
        print("bcd")
        form = SetPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been successfully reset.")
            return redirect('users.login')
    else:
        form = SetPasswordForm(user=user)

    return render(request, 'users/new_password.html', {'form': form})

@login_required
def set_preferences(request):
    # Check if user already has preferences
    try:
        preferences = UserPreferences.objects.get(user=request.user)
        # Pre-fill form with existing data
        form = UserPreferencesForm(instance=preferences)
    except UserPreferences.DoesNotExist:
        # Create new form if no preferences exist
        form = UserPreferencesForm()
        preferences = None

    if request.method == 'POST':
        if preferences:
            # Update existing preferences
            form = UserPreferencesForm(request.POST, instance=preferences)
        else:
            # Create new preferences
            form = UserPreferencesForm(request.POST)

        if form.is_valid():
            preferences = form.save(commit=False)
            preferences.user = request.user
            preferences.save()

            messages.success(request, "Your preferences have been saved successfully!")
            return redirect('users.profile')  # Redirect to profile page after saving

    return render(request, 'users/preferences.html', {'form': form})