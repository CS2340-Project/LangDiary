from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

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
            return redirect('profile')
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
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'template_data': {
            'title': 'User Profile'
        }
    }
    return render(request, 'users/profile.html', context)


def get_profile_picture_url(self):
    if self.profile_picture and hasattr(self.profile_picture, 'url'):
        return self.profile_picture.url
    else:
        return '/static/users/default_profile.jpg'  # Path to a default image
    

@login_required
def delete_profile_picture(request):
    if request.method == 'POST':
        # Get the user's profile
        profile = request.user.profile
        
        # Check if there's a profile picture to delete
        if profile.profile_picture and profile.profile_picture.name != 'default.jpg':
            # Delete the old file from storage
            if os.path.isfile(profile.profile_picture.path):
                os.remove(profile.profile_picture.path)
            
            # Reset to default
            profile.profile_picture = 'profile_pics/default.jpg'
            profile.save()
            
            messages.success(request, 'Your profile picture has been removed.')
        
        return redirect('profile')
    
    # If not a POST request, redirect to profile
    return redirect('profile')