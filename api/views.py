""" api/views.py """
# pylint: disable=redefined-builtin

import os
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.shortcuts import render
from django.contrib.auth import get_user_model

from .models import Project, RiskNote, Survey
from rest_framework.permissions import IsAdminUser
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    SurveySerializer,
    SurveyNestedSerializer,
    RiskNoteSerializer,
    UserSerializer,
    SignInSerializer,
    AudioUploadSerializer
)
from pydub import AudioSegment
from django.conf import settings
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer, ResultReason, CancellationReason, translation


User = get_user_model()

# Url-links to the API endpoints
@api_view(["GET"])
def api_root(request, format=None):
    """ API root view """
    context = {
        "projects_url": reverse("project-list", request=request, format=format),
        "surveys_url": reverse("survey-list", request=request, format=format),
    }
    return render(request, 'api/index.html', context)

# <GET, POST, HEAD, OPTIONS> /api/projects/
class ProjectList(generics.ListCreateAPIView):
    """Class for ProjectList"""
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdminUser()]

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS> /api/projects/<id>/
class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for ProjectDetail"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdminUser()]

# <GET, POST, HEAD, OPTIONS> /api/projects/<id>/surveys/ or /api/surveys/
class SurveyList(generics.ListCreateAPIView):
    """Class for SurveyList"""
    serializer_class = SurveySerializer

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return Survey.objects.filter(project_id=project_id)
        return Survey.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        project_id = self.kwargs.get('project_pk')
        if project_id:
            context['project'] = Project.objects.get(pk=project_id)
        return context

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            project = Project.objects.get(pk=project_id)
            serializer.save(project=project)
        else:
            serializer.save()

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS>
# /api/projects/<project_id>/surveys/<survey_id> or /api/surveys/<id>/
class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for SurveyDetail"""
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

# <GET, POST, HEAD, OPTIONS> /api/surveys/<id>/risk_notes/
# + Supports list of risk_notes as payload
class RiskNoteCreate(generics.ListCreateAPIView):
    """
    Handles the creation and listing of RiskNote objects. 
    Supports a list of RiskNote:s as payload.
    """
    serializer_class = RiskNoteSerializer

    def get_queryset(self):
        survey_id = self.kwargs.get('survey_pk')
        if survey_id:
            return RiskNote.objects.filter(survey_id=survey_id)
        return RiskNote.objects.all()

    def get_serializer_context(self):
        # Pass the survey to the serializer context
        context = super().get_serializer_context()
        survey_id = self.kwargs.get('survey_pk')
        if survey_id:
            context['survey'] = Survey.objects.get(id=survey_id)
        return context
    
    def perform_create(self, serializer):
        survey_id = self.kwargs.get('survey_pk')
        if survey_id:
            survey = Survey.objects.get(pk=survey_id)
            serializer.save(survey=survey)
        else:
            serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RiskNoteDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for RiskNoteDetail"""
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

# <GET, HEAD, OPTIONS> /api/risk_notes/
class RiskNoteList(generics.ListAPIView):
    """Class for RiskNoteList"""
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer

# <PUT/PATCH> /api/risk_notes/<id>/
class RiskNoteUpdate(generics.UpdateAPIView):
    """Class for RiskNoteUpdate"""
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer

# <GET, POST, HEAD, OPTIONS> /api/users/
class UserList(generics.ListCreateAPIView):
    """Class for UserList"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS> /api/users/<id>/
class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for UserDetail"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

# <POST> /api/signin/
class SignIn(generics.CreateAPIView):
    """Class for SignIn"""
    serializer_class = SignInSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

        _, created = User.objects.get_or_create(username=username)

        if created:
            message = f"User '{username}' created and signed in successfully"
            status_code = status.HTTP_201_CREATED
        else:
            message = f"User '{username}' signed in successfully"
            status_code = status.HTTP_200_OK

        return Response({"message": message}, status=status_code)

class TranscribeAudio(generics.CreateAPIView):
    """Class for uploading, converting audio, and transcribing using Azure Speech SDK."""
    serializer_class = AudioUploadSerializer

    def create(self, request, *args, **kwargs):
        # Get the uploaded file from the request
        file = request.FILES.get('audio')
        recognition_language = 'fi-FI'
        target_language = 'en'

        if not file:
            return Response({"error": "Audio file is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Define file paths
        input_path = os.path.join(settings.MEDIA_ROOT, file.name)
        output_path = os.path.join(settings.MEDIA_ROOT, f"{os.path.splitext(file.name)[0]}.wav")

        # Save the uploaded file
        with open(input_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        try:
            # Convert to WAV using pydub
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format="wav")

            if recognition_language == target_language:
                # Perform transcription using Azure Speech SDK
                transcription = self.transcribe_with_azure(output_path, recognition_language)
                if transcription is None:
                    return Response({"error": "Failed to transcribe the audio"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                message = f"Audio file '{file.name}' successfully converted to WAV and transcribed."
                return Response({"message": message, "transcription": transcription}, status=status.HTTP_201_CREATED)
            else:
                transcription = self.transcribe_and_translate(output_path, recognition_language, target_language)
                if transcription is None:
                    return Response({"error": "Failed to translate the audio"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                message = f"Audio file '{file.name}' successfully converted to WAV, transcribed and translated."
                return Response({"message": message, "transcription": transcription}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def transcribe_with_azure(self, wav_file_path, recognition_language):
        try:
            # Initialize the Azure Speech SDK
            speech_key = settings.SPEECH_KEY
            service_region = settings.SPEECH_SERVICE_REGION
            speech_config = SpeechConfig(subscription=speech_key, region=service_region)
            speech_config.speech_recognition_language = recognition_language

            # Create an AudioConfig instance from the WAV file
            audio_config = AudioConfig(filename=wav_file_path)

            # Initialize the recognizer
            recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

            # Perform the transcription
            result = recognizer.recognize_once()

            # Check the result and return the transcription text
            if result.reason == ResultReason.RecognizedSpeech:
                return result.text
            elif result.reason == ResultReason.NoMatch:
                return "No speech could be recognized"
            elif result.reason == ResultReason.Canceled:
                return f"Recognition canceled: {result.cancellation_details.reason}"

        except Exception as e:
            return f"Azure transcription failed: {e}"
    
    def transcribe_and_translate(self, wav_file_path, recognition_language='en-US', target_language='fi'):
        """Translates text using Azure Translator API"""
        try:
            speech_key = settings.SPEECH_KEY
            service_region = settings.SPEECH_SERVICE_REGION
            speech_translation_config = translation.SpeechTranslationConfig(subscription=speech_key, region=service_region)

            speech_translation_config.speech_recognition_language = recognition_language
            speech_translation_config.add_target_language(target_language)

            audio_config = AudioConfig(filename=wav_file_path)

            translation_recognizer = translation.TranslationRecognizer(
                translation_config=speech_translation_config,
                audio_config=audio_config
            )

            translation_recognition_result = translation_recognizer.recognize_once_async().get()

            # Handle the result based on the outcome
            if translation_recognition_result.reason == ResultReason.TranslatedSpeech:
                translated_text = translation_recognition_result.translations[target_language]

                # Return the recognized and translated text
                return translated_text

            elif translation_recognition_result.reason == ResultReason.NoMatch:
                return "error: No speech could be recognized"

            elif translation_recognition_result.reason == ResultReason.Canceled:
                cancellation_details = translation_recognition_result.cancellation_details
                err = f"error: Speech Recognition canceled: {cancellation_details.reason}"
                if cancellation_details.reason == CancellationReason.Error:
                    return f"{err}, details: {cancellation_details.error_details}"
                else:
                    return err


        except Exception as e:
            return f"Translation failed: {e}"