""" api/tests/unit/test_views.py """
# pylint: disable=attribute-defined-outside-init

import json
from unittest.mock import patch, MagicMock
from azure.cognitiveservices.speech import ResultReason, CancellationReason
import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

class TestTranscribeAudioView:
    """Test cases for TranscribeAudio view"""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_file):
        """Setup method"""
        self.url = reverse('transcribe_audio')
        self.mock_file = mock_file

    def test_no_file_uploaded(self, client):
        """Test when no audio file is uploaded."""
        response = client.post(self.url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "Audio file is required"}

    @patch('pydub.AudioSegment.from_file')
    @patch('api.views.TranscribeAudio.transcribe_with_azure')
    @patch('azure.cognitiveservices.speech.translation.TranslationRecognizer')
    def test_successful_transcription_with_translation(
        self, mock_recognizer, mock_transcribe_with_azure, mock_audio_segment, client
    ):
        """Test for successful transcription and translation."""

        mock_transcribe_with_azure.return_value = "This is a transcription."

        mock_translation = mock_recognizer.return_value
        mock_result = MagicMock()
        mock_result.reason = ResultReason.TranslatedSpeech
        mock_result.translations = {'en': 'This is a translation.'}

        mock_translation.recognize_once_async.return_value.get.return_value = mock_result

        response = client.post(
            self.url,
            {
                'audio': self.mock_file,
                'recordingLanguage': 'en-US',
                'translationLanguages': json.dumps(['en'])
            },
            format='multipart'
        )

        expected_message = (
            "Audio file 'test_audio.mp3' successfully "
            "converted to WAV, transcribed and translated."
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "message": expected_message,
            "transcription": "This is a transcription.",
            "translations": {'en': 'This is a translation.'}
        }

        mock_audio_segment.assert_called_once()
        mock_transcribe_with_azure.assert_called_once()
        mock_recognizer.assert_called_once()

    @patch('pydub.AudioSegment.from_file')
    @patch('api.views.TranscribeAudio.transcribe_with_azure')
    @patch('azure.cognitiveservices.speech.translation.TranslationRecognizer')
    def test_transcription_canceled(
        self, mock_recognizer, mock_transcribe_with_azure, mock_audio_segment, client
    ):
        """Test for transcription and translation failure"""

        mock_transcribe_with_azure.return_value = "This is a transcription."

        mock_translation = mock_recognizer.return_value
        mock_result = MagicMock()
        mock_result.reason = ResultReason.Canceled

        mock_cancellation_details = MagicMock()
        mock_cancellation_details.reason = CancellationReason.Error
        mock_cancellation_details.error_details = "Error details"

        mock_result.cancellation_details = mock_cancellation_details

        mock_translation.recognize_once_async.return_value.get.return_value = mock_result

        response = client.post(
            self.url,
            {
                'audio': self.mock_file,
                'recordingLanguage': 'en-US',
                'translationLanguages': json.dumps(['en'])
            },
            format='multipart'
        )

        expected_error_message = (
        "error: Speech Recognition canceled: CancellationReason.Error, details: Error details"
        )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {
            "error": "Failed to translate the audio",
            "returnvalue": expected_error_message
        }

        mock_recognizer.assert_called_once()
        mock_audio_segment.assert_called_once()

    @patch('pydub.AudioSegment.from_file')
    @patch('api.views.TranscribeAudio.transcribe_with_azure')
    @patch('azure.cognitiveservices.speech.translation.TranslationRecognizer')
    def test_transcription_no_match(
        self, mock_recognizer, mock_transcribe_with_azure, mock_audio_segment, client
    ):
        """Test for 'No speech could be recognized' case"""

        mock_transcribe_with_azure.return_value = "This is a transcription."

        mock_translation = mock_recognizer.return_value
        mock_result = MagicMock()
        mock_result.reason = ResultReason.NoMatch
        mock_translation.recognize_once_async.return_value.get.return_value = mock_result

        response = client.post(
            self.url,
            {
                'audio': self.mock_file,
                'recordingLanguage': 'en-US',
                'translationLanguages': json.dumps(['en'])
            },
            format='multipart'
        )

        expected_message = "error: No speech could be recognized"
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {
            "error": "Failed to translate the audio",
            "returnvalue": expected_message
        }
        mock_audio_segment.assert_called_once()

    @patch('pydub.AudioSegment.from_file')
    @patch('api.views.TranscribeAudio.transcribe_with_azure')
    @patch('azure.cognitiveservices.speech.translation.TranslationRecognizer')
    def test_translation_value_error(
        self, mock_recognizer, mock_transcribe_with_azure, mock_audio_segment, client
    ):
        """Test for exception during translation"""

        mock_transcribe_with_azure.return_value = "This is a transcription."

        mock_recognizer.side_effect = ValueError("Some translation error")

        response = client.post(
            self.url,
            {
                'audio': self.mock_file,
                'recordingLanguage': 'en-US',
                'translationLanguages': json.dumps(['en'])
            },
            format='multipart'
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {
            "error": "Failed to translate the audio",
            "returnvalue": "Translation failed: Some translation error"
        }
        mock_audio_segment.assert_called_once()

    @patch('pydub.AudioSegment.from_file')
    @patch('api.views.TranscribeAudio.transcribe_with_azure')
    @patch('azure.cognitiveservices.speech.translation.TranslationRecognizer')
    def test_transcription_with_no_valid_translation_languages(
        self, mock_recognizer, mock_transcribe_with_azure, mock_audio_segment, client
    ): # pylint: disable=unused-argument
        """Test for transcription with no valid translation languages"""

        mock_transcribe_with_azure.return_value = "This is a transcription."

        response = client.post(
            self.url,
            {
                'audio': self.mock_file,
                'recordingLanguage': 'en-US',
                'translationLanguages': json.dumps('en')
            },
            format='multipart'
        )

        expected_message = (
            "Audio file 'test_audio.mp3' successfully "
            "converted to WAV, transcribed and translated."
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "message": expected_message,
            "transcription": "This is a transcription.",
            "translations": {}
        }
        mock_audio_segment.assert_called_once()
