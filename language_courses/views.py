from django.shortcuts import render

def home(request):
    return render(request, 'language_courses/home.html')

