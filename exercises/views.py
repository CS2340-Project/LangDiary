from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.shortcuts import render, redirect
from .models import Exercise
from django.contrib import messages
from .forms import ExerciseForm
from django.utils import timezone
from datetime import timedelta
import json
import random
from LangDiary.settings import BASE_DIR

@login_required
def index(request):
    user = request.user
    profile = user.profile
    lang = user.profile.language_learning
    exercises = Exercise.objects.filter(user=user)

    # msgs = get_messages(request)
    # for message in msgs:
    #     print(f"Message: {message} (Level: {message.level}, Tags: {message.tags})")


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

json_file_path = BASE_DIR / 'exercises' / 'static' / 'json' / 'exercises.json'

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
    # print(f"PROFILE : {profile.language_level}")
    # print("level:", profile.language_level)

    if profile.language_level == 'Undecided':
        messages.error(request, "Choose language level to create exercises")
        return redirect('exercises:index')

    prompt = get_random_prompt(profile.language_level)
    # print(f"PROMPT SUKA: {prompt}")
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
