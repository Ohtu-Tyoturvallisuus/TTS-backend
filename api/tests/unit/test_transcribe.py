""" api/tests/unit/test_views.py """

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

client = APIClient()

def test_transcribe_audio_no_file():
    """Test TranscribeAudio view with no file provided"""
    url = reverse('transcribe_audio')
    response = client.post(url, {}, format='multipart')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == "Audio file is required"
