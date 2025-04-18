from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from .models import Exercise
from django.conf import settings
from django.contrib import messages
from .forms import ExerciseForm
from django.utils import timezone
from datetime import timedelta
import json, os, random
from LangDiary.settings import BASE_DIR
@login_required
def index(request):
    user = request.user
    profile = user.profile
    lang = user.profile.language_learning
    exercises = Exercise.objects.filter(user=user)
    if not exercises.exists():
        return render(request, 'exercises/index.html', {
            'exercises': [],
            'profile': profile
            #'profile': profile_data
        })
    return render(request, 'exercises/index.html', {
        "lang": lang,
        "exercises": exercises,
        "due_date":timezone.now().date() + timedelta(days=7)
    })

json_file_path = BASE_DIR / 'exercises/static' / 'json' / 'exercises.json'

def load_json_data():
    try:
        with open(json_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file at {json_file_path} was not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: The JSON data could not be decoded.")
        return {}
    
def get_random_prompt(user_skill):
    data = load_json_data()
    if not data:
        return None
    matching_prompts = [exercise for exercise in data.values() if exercise['skill'] == user_skill]
    if not matching_prompts:
        return None 
    selected_prompt = random.choice(matching_prompts)
    return selected_prompt
@login_required
def create_exercise(request):
    profile = request.user.profile
    prompt = get_random_prompt(profile.language_level)
    print(prompt)
    if True: #profile.exercise_ready:
        # for testing purposes exercises cool down is 0
        '''if profile.last_exercise_date and (timezone.now().date() - profile.last_exercise_date).days < 7:
            profile.exercise_ready = False 
            profile.save()
            messages.error(request, "You can only create a new exercise once a week.")
            return redirect('some_other_page')'''
        Exercise.objects.create(user=request.user, type=prompt['type'], prompt=prompt['prompt'], skill=prompt['skill'], deadline=timezone.now().date())
        profile.last_exercise_date = timezone.now().date()
        profile.exercise_ready = False
        profile.save()

        messages.success(request, "Exercise created successfully!")
        return redirect('exercises:create_page')
@login_required
def create_page(request):
    user = request.user
    latest_exercise = Exercise.objects.filter(user=user).order_by('-created_at').first()
    prompt = latest_exercise.prompt
    print(latest_exercise)
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            latest_exercise.content = request.POST.get("content")
            latest_exercise.save() 
            print(latest_exercise)
            
            return redirect('exercises:index') 

    else:
        form = ExerciseForm()

    return render(request, 'exercises/create_exercise_page.html', {'form': form, "prompt": prompt})
