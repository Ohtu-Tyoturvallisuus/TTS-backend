""" api/views/utils_views.py """

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

# Url-links to the API endpoints
@api_view(["GET"])
def api_root(request, format=None): # pylint: disable=redefined-builtin
    """ API root view """
    context = {
        "projects_url": reverse("project-list", request=request, format=format),
        "surveys_url": reverse("survey-list", request=request, format=format),
    }
    return render(request, 'api/index.html', context)
