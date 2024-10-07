""" api/tests/unit/test_views.py """

import os
from unittest import mock
import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from pydub import AudioSegment

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    yield
    input_path = os.path.join(settings.MEDIA_ROOT, 'test.mp3')
    output_path = os.path.join(settings.MEDIA_ROOT, 'test.wav')
    if os.path.exists(input_path):
        os.remove(input_path)
    if os.path.exists(output_path):
        os.remove(output_path)

@mock.patch('pydub.AudioSegment.from_file')
@mock.patch('azure.cognitiveservices.speech.audio.AudioConfig')
@mock.patch('api.views.TranscribeAudio.transcribe_with_azure')
@mock.patch('api.views.TranscribeAudio.transcribe_and_translate')
@mock.patch('builtins.open', new_callable=mock.mock_open)
def test_successful_transcription(
    mock_audiosegment,
    mock_audioconfig,
    mock_transcribe_with_azure,
    mock_transcribe_and_translate,
    mock_open,
    client):
    """Test successful transcription"""

    mock_audiosegment_instance = mock.MagicMock()
    mock_audiosegment.return_value = mock_audiosegment_instance
    mock_audiosegment_instance.export.return_value = None

    mock_transcribe_with_azure.return_value = "Test transcription"
    mock_transcribe_and_translate.return_value = "Translated text"

    mock_audioconfig.return_value = mock.MagicMock()

    mock_file = SimpleUploadedFile('test.mp3', b'file_content', content_type='audio/mpeg')

    with mock.patch('os.path.join', return_value='/mocked/path/test_audio.wav'):
        url = reverse('transcribe_audio')
        response = client.post(url, {'audio': mock_file}, format='multipart')

    mock_open.assert_called_once_with('/mocked/path/test_audio.wav', 'wb+')

    assert response.status_code == status.HTTP_201_CREATED
    assert 'transcription' in response.data
    assert response.data['transcription'] == "Test transcription"

def test_transcribe_audio_no_file(client):
    """Test TranscribeAudio view with no file provided"""
    url = reverse('transcribe_audio')
    response = client.post(url, {}, format='multipart')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == "Audio file is required"
