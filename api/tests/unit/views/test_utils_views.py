""" api/tests/unit/views/test.utils_views.py """

import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

def test_api_root(client):
    """Test API root view"""
    response = client.get(reverse('api-root'))
    assert response.status_code == status.HTTP_200_OK
    assert 'projects_url' in response.context
    assert 'surveys_url' in response.context
