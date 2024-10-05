""" api/tests/unit/test_views.py """

from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

client = APIClient()

@patch('api.views.AudioSegment.from_file')
def test_transcribe_audio_no_file(mock_audio_segment): # pylint: disable=unused-argument
    """Test TranscribeAudio view with no file provided"""
    url = reverse('transcribe_audio')
    response = client.post(url, {}, format='multipart')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == "Audio file is required"