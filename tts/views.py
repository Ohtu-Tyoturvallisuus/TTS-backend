"""
This module contains view functions for the TTS application.
"""

from django.shortcuts import render
from django.urls import reverse

def index(request):
    """
    Render the index page with the API link.
    """
    context = {
        'api_link': reverse('api-root')
    }
    return render(request, 'index.html', context)
