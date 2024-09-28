from django.shortcuts import render
from django.urls import reverse

def index(request):
    context = {
        'api_link': reverse('api-root')
    }
    return render(request, 'index.html', context)