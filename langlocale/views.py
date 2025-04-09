from django.shortcuts import render
from .utils.langlocale import get_data

# Create your views here.
def index(request):
    template_data = {'title': 'LangLocales'}
    data = get_data()
    print(data)
    return render(request, 'langlocale/index.html', {
        'place_data': data
    })