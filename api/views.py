""" api/views.py """
# pylint: disable=redefined-builtin

import os
import uuid
import json
import random
import string
import jwt
from rest_framework import (
    generics,
    status,
    permissions
)
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponse

from pydub import AudioSegment
from azure.cognitiveservices.speech import (
    SpeechConfig,
    AudioConfig,
    SpeechRecognizer,
    ResultReason,
    CancellationReason,
    translation
)
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError, HttpResponseError, ResourceNotFoundError

from .models import Project, RiskNote, Survey
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    SurveySerializer,
    RiskNoteSerializer,
    UserSerializer,
    SignInSerializer,
    AudioUploadSerializer
)

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
        if not project_id:
            raise serializers.ValidationError(
                {"project": "A project is required to create a survey."}
            )
        project = get_object_or_404(Project, pk=project_id)
        serializer.save(project=project)

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS>
# /api/projects/<project_id>/surveys/<survey_id> or /api/surveys/<id>/
class SurveyDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for SurveyDetail"""
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

# <GET, POST, HEAD, OPTIONS> /api/surveys/<id>/risk_notes/
# or /api/projects/<project_id>/surveys/<survey_id>/risk_notes/
# + Supports list of risk_notes as payload
class RiskNoteCreate(generics.ListCreateAPIView):
    """
    Handles the creation and listing of RiskNote objects. 
    Supports a list of RiskNote:s as payload.
    """
    serializer_class = RiskNoteSerializer

    def get_queryset(self):
        survey_id = self.kwargs.get('survey_pk') # no need to check if survey_id is None
        return RiskNote.objects.filter(survey_id=survey_id)

    def get_serializer_context(self):
        # Pass the survey to the serializer context
        context = super().get_serializer_context()
        survey_id = self.kwargs.get('survey_pk')
        if survey_id:
            context['survey'] = get_object_or_404(Survey, id=survey_id)
        return context

    def perform_create(self, serializer):
        survey_id = self.kwargs.get('survey_pk') # no need to check if survey_id is None
        survey = get_object_or_404(Survey, pk=survey_id)
        serializer.save(survey=survey)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# <GET, PUT, PATCH, DELETE, HEAD, OPTIONS>
# /api/projects/<project_id>/surveys/<survey_id>/risk_notes/<id>/
class RiskNoteDetail(generics.RetrieveUpdateDestroyAPIView):
    """Class for RiskNoteDetail"""
    queryset = RiskNote.objects.all()
    serializer_class = RiskNoteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = 'pk'

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
        id = request.data.get('id')
        guest = request.data.get('guest')
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

        _, created = User.objects.get_or_create(username=username)

        if guest:
            characters = string.ascii_letters + string.digits
            id = ''.join(random.choice(characters) for _ in range(64))

        payload = {
            'username': username,
            'user_id': id,
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        if created:
            message = f"User '{username}' created and signed in successfully"
            status_code = status.HTTP_201_CREATED
        else:
            message = f"User '{username}' signed in successfully"
            status_code = status.HTTP_200_OK

        return Response({"message": message, 'access_token': token}, status=status_code)

# <POST> /api/transcribe/
class TranscribeAudio(generics.CreateAPIView):
    """Class for uploading, converting audio, and transcribing using Azure Speech SDK."""
    serializer_class = AudioUploadSerializer

    def create(self, request, *args, **kwargs):
        # Get the uploaded file from the request
        file = request.FILES.get('audio')
        recognition_language = request.POST.get('recordingLanguage')
        target_languages = request.POST.get('translationLanguages')
        if target_languages:
            target_languages = json.loads(target_languages)
        else:
            target_languages = []

        if not isinstance(target_languages, list):
            target_languages = []

        if not file:
            return Response({"error": "Audio file is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Define file paths
        input_path = os.path.join(settings.BASE_DIR, file.name)
        output_path = os.path.join(settings.BASE_DIR, f"{os.path.splitext(file.name)[0]}.wav")

        # Save the uploaded file
        with open(input_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Convert to WAV using pydub
        AudioSegment.from_file(input_path).export(output_path, format="wav")
        # Perform transcription using Azure Speech SDK
        transcription = self.transcribe_with_azure(output_path, recognition_language)
        if transcription is None or transcription.startswith('error'):
            return Response(
                {"error": "Failed to transcribe the audio", "returnvalue": transcription},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        translations = self.transcribe_and_translate(
            output_path,
            recognition_language,
            target_languages
        )
        if isinstance(translations, str):
            return Response(
                {"error": "Failed to translate the audio", "returnvalue": translations},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        message = (
            f"Audio file '{file.name}' successfully converted to WAV, "
            "transcribed and translated."
        )
        return Response(
            {"message": message, "transcription": transcription, "translations": translations},
            status=status.HTTP_201_CREATED
        )

    def transcribe_with_azure(self, wav_file_path, recognition_language):
        """Method for transcribing speech to text written in the same language"""
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
            if result.reason == ResultReason.NoMatch:
                return "error: No speech could be recognized"
            if result.reason == ResultReason.Canceled:
                return f"error: Recognition canceled: {result.cancellation_details.reason}"
            raise ValueError("Unexpected result reason")

        except ValueError as e:
            return f"Azure transcription failed: {e}"

    def transcribe_and_translate(
        self,
        wav_file_path,
        recognition_language,
        target_languages
    ):
        """Translates text using Azure Translator API"""
        try:
            if target_languages == []:
                return {}
            speech_key = settings.SPEECH_KEY
            service_region = settings.SPEECH_SERVICE_REGION
            speech_translation_config = translation.SpeechTranslationConfig(
                subscription=speech_key,
                region=service_region
            )

            speech_translation_config.speech_recognition_language = recognition_language
            for language in target_languages:
                speech_translation_config.add_target_language(language)

            audio_config = AudioConfig(filename=wav_file_path)

            translation_recognizer = translation.TranslationRecognizer(
                translation_config=speech_translation_config,
                audio_config=audio_config
            )

            translation_recognition_result = translation_recognizer.recognize_once_async().get()

            # Handle the result based on the outcome
            if translation_recognition_result.reason == ResultReason.TranslatedSpeech:
                translations = {}
                for language in target_languages:
                    translations[language] = str(
                        translation_recognition_result.translations[language]
                    )

                # Return the recognized and translated text
                return translations

            if translation_recognition_result.reason == ResultReason.NoMatch:
                return "error: No speech could be recognized"

            if translation_recognition_result.reason == ResultReason.Canceled:
                cancellation_details = translation_recognition_result.cancellation_details
                err = f"error: Speech Recognition canceled: {cancellation_details.reason}"
                if cancellation_details.reason == CancellationReason.Error:
                    return f"{err}, details: {cancellation_details.error_details}"
                return err
            raise ValueError("Unexpected result reason")

        except ValueError as e:
            return f"Translation failed: {e}"

# <POST> /api/upload-image/
class UploadImage(generics.CreateAPIView):
    """Class for uploading images to Azure Blob Storage"""

    def post(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response(
                {'status': 'error', 'message': 'No image file provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        image = request.FILES['image']

        if not self.validate_image(image):
            return Response(
                {'status': 'error', 'message': 'Invalid file type. Only images are allowed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create BlobServiceClient
        try:
            blob_service_client = BlobServiceClient(
                account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
                credential=settings.AZURE_STORAGE_ACCOUNT_KEY
            )
            container_client = blob_service_client.get_container_client(
                settings.AZURE_CONTAINER_NAME
            )

            # Generate a unique blob name
            blob_name = f"images/{uuid.uuid4()}_{image.name}"


            # Upload the image to the blob
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(image, overwrite=True)

            # Construct the blob URL
            blob_url = (
                f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/"
                f"{settings.AZURE_CONTAINER_NAME}/{blob_name}"
            )

            return Response({'status': 'success', 'url': blob_url}, status=status.HTTP_201_CREATED)

        except (HttpResponseError, AzureError) as e:
            # Consolidate all errors here
            if isinstance(e, HttpResponseError):
                error_message = 'HTTP error during Azure Blob Storage operation: '
            else:
                error_message = 'Azure Blob Storage error: '

            return Response(
                {'status': 'error', 'message': error_message + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def validate_image(self, image):
        """Validate image file type"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in valid_extensions:
            return False
        return True

# <GET> /api/retrieve-image/?blob_name=<blob_name>/
class RetrieveImage(generics.RetrieveAPIView):
    """Class for retrieving images from Azure Blob Storage"""

    def get(self, request, *args, **kwargs):
        blob_name = request.query_params.get('blob_name')

        if not blob_name:
            return Response(
                {'status': 'error', 'message': 'No blob name provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create BlobServiceClient
        try:
            blob_service_client = BlobServiceClient(
                account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
                credential=settings.AZURE_STORAGE_ACCOUNT_KEY
            )
            container_client = blob_service_client.get_container_client(
                settings.AZURE_CONTAINER_NAME
            )
        except (ResourceNotFoundError, HttpResponseError, AzureError) as e:
            if isinstance(e, ResourceNotFoundError):
                error_message = 'Container not found.'
                error_status = status.HTTP_404_NOT_FOUND
            elif isinstance(e, HttpResponseError):
                error_message = f'HTTP error: {str(e)}'
                error_status = status.HTTP_400_BAD_REQUEST
            else:
                error_message = f'Azure service error: {str(e)}'
                error_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(
                {'status': 'error', 'message': error_message},
                status=error_status
            )

        try:
            # Get the Blob Client for the image
            blob_client = container_client.get_blob_client(blob_name)

            # Download the image content
            blob_data = blob_client.download_blob()
            image_data = blob_data.readall()  # Read the content of the blob as binary

            # Determine the file's content type
            content_type = self.get_content_type(blob_name)

            # Return the image as an HttpResponse with the appropriate content type
            return HttpResponse(image_data, content_type=content_type)

        except (ResourceNotFoundError, HttpResponseError, AzureError) as e:
            if isinstance(e, ResourceNotFoundError):
                error_message = 'Image not found.'
                error_status = status.HTTP_404_NOT_FOUND
            elif isinstance(e, HttpResponseError):
                error_message = f'HTTP error: {str(e)}'
                error_status = status.HTTP_400_BAD_REQUEST
            else:
                error_message = f'Azure service error: {str(e)}'
                error_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(
                {'status': 'error', 'message': error_message},
                status=error_status
            )

    def get_content_type(self, blob_name):
        """Helper function to determine content type based on file extension"""
        if blob_name.lower().endswith('.jpg') or blob_name.lower().endswith('.jpeg'):
            return 'image/jpeg'
        if blob_name.lower().endswith('.png'):
            return 'image/png'
        if blob_name.lower().endswith('.gif'):
            return 'image/gif'
        return 'application/octet-stream'  # Default binary data type if unknown

# <GET> /api/retrieve_params/
class RetrieveParams(generics.RetrieveAPIView):
    """Class for retrieving client and tenant id params"""

    def get(self, request, *args, **kwargs):
        return Response({
            'client_id': settings.CLIENT_ID,
            'tenant_id': settings.TENANT_ID,
            'status': status.HTTP_200_OK
        })
