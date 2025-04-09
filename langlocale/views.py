from django.shortcuts import render

# Create your views here.
def index(request):
    template_data = {'title': 'LangLocales'}
    return render(request, 'langlocale/index.html', {
        'template_data': template_data
    })