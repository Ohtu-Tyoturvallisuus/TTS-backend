""" api/views/azure_views.py """

import json
import os
import uuid
import requests
from azure.cognitiveservices.speech import (
    AudioConfig,
    CancellationReason,
    ResultReason,
    SpeechConfig,
    SpeechRecognizer,
    translation
)
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import (
    AzureError,
    HttpResponseError,
    ResourceNotFoundError
)
from django.conf import settings
from django.http import HttpResponse
from pydub import AudioSegment
from requests.exceptions import (
    HTTPError,
    RequestException,
    Timeout
)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import AudioUploadSerializer

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
class UploadImages(generics.CreateAPIView):
    """Class for uploading images to Azure Blob Storage"""

    def post(self, request, *args, **kwargs):
        # Collect all files from request.FILES
        images = [file for key, file in request.FILES.items()]
        if not images:
            return Response(
                {'status': 'error', 'message': 'No image files provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_urls = []

        try:
            blob_service_client = BlobServiceClient(
                account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
                credential=settings.AZURE_STORAGE_ACCOUNT_KEY
            )
            container_client = blob_service_client.get_container_client(
                settings.AZURE_CONTAINER_NAME
            )

            for image in images:
                if not self.validate_image(image):
                    return Response(
                        {
                            'status': 'error',
                            'message': (
                                f'Invalid file type for {image.name}. '
                                'Only images are allowed.'
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
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
                uploaded_urls.append(blob_url)

            return Response(
                {'status': 'success', 'urls': uploaded_urls},
                status=status.HTTP_201_CREATED
            )

        except (HttpResponseError, AzureError) as e:
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
        return ext in valid_extensions

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

# Helper function to get Azure translation parameters
def get_azure_translation_params():
    """Helper function to get Azure translation parameters"""
    return {
        'key': settings.TRANSLATOR_KEY,
        'endpoint': settings.TRANSLATOR_ENDPOINT,
        'location': settings.TRANSLATOR_SERVICE_REGION
    }

# <POST> /api/translate/
class TranslateText(generics.CreateAPIView):
    """Class for translating text using Azure Translator API"""
    def create(self, request, *args, **kwargs):
        azure_params = get_azure_translation_params()

        source_language = request.data.get('from', 'fi')
        target_languages = request.data.get('to', [])
        text = request.data.get('text', None)

        if not isinstance(target_languages, list) or not target_languages:
            return Response(
                {'error': 'Invalid or missing "to" parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not text:
            return Response(
                {'error': 'Invalid or missing "text" parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = self.translate_text(azure_params, source_language, target_languages, text)
            return Response(response, status=status.HTTP_200_OK)
        except (HTTPError, Timeout, RequestException) as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Helper function to translate text using Azure Translator API
    def translate_text(self, azure_params, source_language, target_languages, text):
        """Translate text using Azure Translator API"""
        params = {
            'api-version': '3.0',
            'from': source_language,
            'to': target_languages
        }

        headers = {
            'Ocp-Apim-Subscription-Key': azure_params['key'],
            'Ocp-Apim-Subscription-Region': azure_params['location'],
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        body = [{'text': text}]

        try:
            response = requests.post(
                f"{azure_params['endpoint']}/translate",
                params=params,
                headers=headers,
                json=body,
                timeout=10
            )
            response.raise_for_status()
            response_data = response.json()

            return {
                translation['to']: translation['text']
                for translation in response_data[0]['translations']
            }
        except RequestException as e:
            error_message = f'Request error occurred: {str(e)}'
            raise RequestException(error_message) from e


class GetProjectsView(APIView):
    """
    API view to retrieve projects from ERP.
    """

    # Storing the token temporarily for testing purposes
    access_token = None  # Global variable to store the access token for testing

    def get_access_token(self, resource):
        """
        Helper method to get an access token from Azure AD.
        """
        token_url = f"https://login.microsoftonline.com/{settings.ERP_TENANT_ID}/oauth2/token"
        payload = {
            'client_id': settings.ERP_CLIENT_ID,
            'client_secret': settings.ERP_CLIENT_SECRET,
            'grant_type': 'client_credentials',
            'resource': resource,
        }
        try:
            token_response = requests.post(token_url, data=payload)
            token_response.raise_for_status()
            return token_response.json().get('access_token')
        except requests.RequestException as e:
            raise Exception(f"Authentication failed: {str(e)}")

    def fetch_projects(self, access_token, resource):
        """
        Helper method to fetch project data from Dynamics 365 FO.
        """
        projects_url = (
            f"{resource}/data/Projects?cross-company=true"
            f"&$filter=ProjectStage eq Microsoft.Dynamics.DataEntities.ProjStatus'InProcess'"
            f"&$select=ProjectID,dataAreaId,ProjectName,DimensionDisplayValue,WorkerResponsiblePersonnelNumber,CustomerAccount"
            f"&$top=100"
        )
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        try:
            projects_response = requests.get(projects_url, headers=headers)
            projects_response.raise_for_status()
            return projects_response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch projects: {str(e)}")

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to fetch projects from Dynamics 365 FO.
        """
        # Use the stored access token if available, otherwise get a new token
        if not self.access_token:
            # Determine environment (production or sandbox)
            environment = request.GET.get('environment', 'production')
            resource = settings.ERP_SANDBOX_RESOURCE if environment == 'sandbox' else settings.ERP_RESOURCE
            
            # Step 1: Get access token
            try:
                self.access_token = self.get_access_token(resource)  # Store the token for future use
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Step 2: Fetch projects using the stored token
        try:
            projects_data = self.fetch_projects(self.access_token, resource)
            projects = projects_data.get('value', [])  # Projects are under 'value' in the response
            
            # Extract required fields from projects
            project_list = []
            for project in projects:
                project_info = {
                    'ProjectID': project.get('ProjectID'),
                    'dataAreaId': project.get('dataAreaId'),
                    'ProjectName': project.get('ProjectName'),
                    'DimensionDisplayValue': project.get('DimensionDisplayValue'),
                    'WorkerResponsiblePersonnelNumber': project.get('WorkerResponsiblePersonnelNumber', ''),
                    'CustomerAccount': project.get('CustomerAccount', ''),
                }
                project_list.append(project_info)
            
            return Response(project_list, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
