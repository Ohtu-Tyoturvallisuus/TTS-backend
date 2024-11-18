""" api/tests/unit/views/azure_views_tests/test.azure_views.py """
# pylint: disable=attribute-defined-outside-init

import io
from unittest.mock import patch, MagicMock
import pytest
from azure.core.exceptions import (
    AzureError,
    HttpResponseError,
    ResourceNotFoundError
)
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from requests.exceptions import RequestException
from rest_framework import status
from rest_framework.test import APITestCase

from api.views import RetrieveImage

pytestmark = pytest.mark.django_db

class TestUploadImagesView(TestCase):
    """Tests UploadImage view"""

    def setup_method(self, client):
        """Setup method"""
        self.client = client
        self.url = '/api/upload-images/'

    def test_missing_image_file(self):
        """Test case where no image file is provided."""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'No image files provided.')

    @patch('api.views.azure_views.BlobServiceClient')
    def test_invalid_image_type(self, mock_blob_service_client):
        """Test case where an invalid file type is provided."""
        mock_blob_service = MagicMock()
        mock_container_client = MagicMock()
        mock_blob_service_client.return_value = mock_blob_service
        mock_blob_service.get_container_client.return_value = mock_container_client

        file = io.BytesIO(b"fake image data")
        file.name = 'test.txt'

        response = self.client.post(self.url, {'image': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'],
            f'Invalid file type for {file.name}. Only images are allowed.'
        )

    @patch('api.views.azure_views.BlobServiceClient')
    def test_successful_image_upload(self, mock_blob_service_client):
        """Test successful image upload."""
        mock_blob_service = MagicMock()
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()

        mock_blob_service_client.return_value = mock_blob_service
        mock_blob_service.get_container_client.return_value = mock_container_client
        mock_container_client.get_blob_client.return_value = mock_blob_client

        file = io.BytesIO(b"fake image data")
        file.name = 'test.jpg'

        response = self.client.post(self.url, {'image': file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('urls', response.data)
        mock_blob_client.upload_blob.assert_called_once()

    @patch('api.views.azure_views.BlobServiceClient')
    def test_successful_multiple_image_upload(self, mock_blob_service_client):
        """Test successful multiple image upload."""
        mock_blob_service = MagicMock()
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()

        mock_blob_service_client.return_value = mock_blob_service
        mock_blob_service.get_container_client.return_value = mock_container_client
        mock_container_client.get_blob_client.return_value = mock_blob_client

        file1 = io.BytesIO(b"fake image data 1")
        file1.name = 'test1.jpg'
        file2 = io.BytesIO(b"fake image data 2")
        file2.name = 'test2.jpg'

        response = self.client.post(
            self.url,
            {'image1': file1, 'image2': file2},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('urls', response.data)
        print(response.data['urls'])
        self.assertEqual(len(response.data['urls']), 2)
        self.assertEqual(mock_blob_client.upload_blob.call_count, 2)

    @patch('api.views.azure_views.BlobServiceClient')
    def test_http_error_during_upload(self, mock_blob_service_client):
        """Test HTTP error during image upload to Azure Blob Storage."""
        mock_blob_service = MagicMock()
        mock_blob_service.get_container_client.side_effect = HttpResponseError("HTTP error")
        mock_blob_service_client.return_value = mock_blob_service

        file = io.BytesIO(b"fake image data")
        file.name = 'test.jpg'

        response = self.client.post(self.url, {'image': file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(
            response.data['message'],
            'HTTP error during Azure Blob Storage operation: HTTP error'
        )

    @patch('api.views.azure_views.BlobServiceClient')
    def test_azure_error_during_upload(self, mock_blob_service_client):
        """Test Azure SDK error during image upload."""
        mock_blob_service = MagicMock()
        mock_blob_service.get_container_client.side_effect = AzureError("Azure error")
        mock_blob_service_client.return_value = mock_blob_service

        file = io.BytesIO(b"fake image data")
        file.name = 'test.jpg'

        response = self.client.post(self.url, {'image': file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['message'], 'Azure Blob Storage error: Azure error')

class TestRetrieveImageView(APITestCase):
    """Tests RetrieveImage view"""

    def setUp(self):
        """Setup method"""
        self.url = reverse('retrieve_image')
        self.blob_name = 'test_image.jpg'

        self.blob_service_patcher = patch('api.views.azure_views.BlobServiceClient')
        self.mock_blob_service = self.blob_service_patcher.start()

        self.mock_container_client = MagicMock()
        self.mock_blob_service.return_value.get_container_client.return_value = (
            self.mock_container_client
        )

        self.addCleanup(self.blob_service_patcher.stop)

    def test_missing_blob_name(self):
        """Test case where no blob name is provided"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'status': 'error',
            'message': 'No blob name provided.'
        })

    def test_container_not_found(self):
        """Test container not found"""
        self.mock_blob_service.side_effect = ResourceNotFoundError("Container not found")

        response = self.client.get(self.url, {'blob_name': self.blob_name})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'status': 'error',
            'message': 'Container not found.'
        })

    def test_http_response_error_during_blob_service_client_creation(self):
        """Test case for handling HTTP response error during BlobServiceClient creation"""
        self.mock_blob_service.side_effect = HttpResponseError("HTTP error")

        response = self.client.get(self.url, {'blob_name': self.blob_name})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'status': 'error',
            'message': 'HTTP error: HTTP error'
        })

    def test_http_response_error(self):
        """Test case for handling HTTP response error during blob retrieval"""
        self.mock_container_client.get_blob_client.side_effect = HttpResponseError("HTTP error")

        response = self.client.get(self.url, {'blob_name': self.blob_name})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'status': 'error',
            'message': 'HTTP error: HTTP error'
        })

    @patch('api.views.azure_views.BlobServiceClient.get_container_client')
    def test_blob_not_found(self, mock_get_container_client):
        """Test blob not found"""
        workaround = mock_get_container_client
        lint = workaround
        mock_get_container_client = lint
        mock_blob_client = MagicMock()
        mock_blob_client.download_blob.side_effect = ResourceNotFoundError("Blob not found")
        self.mock_container_client.get_blob_client.return_value = mock_blob_client

        response = self.client.get(self.url, {'blob_name': self.blob_name})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'status': 'error',
            'message': 'Image not found.'
        })

    @patch('api.views.azure_views.BlobServiceClient')
    def test_successful_blob_retrieval(self, mock_blob_service_class):
        """Test case where blob retrieval succeeds"""
        mock_container_client = MagicMock()
        mock_blob_client = MagicMock()

        mock_blob_client.download_blob.return_value.readall.return_value = b'binary_image_data'
        mock_container_client.get_blob_client.return_value = mock_blob_client
        mock_blob_service_class.return_value.get_container_client.return_value = (
            mock_container_client
        )

        response = self.client.get(self.url, {'blob_name': self.blob_name})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'binary_image_data')
        self.assertEqual(response['Content-Type'], 'image/jpeg')

    @patch('api.views.azure_views.BlobServiceClient')
    def test_azure_service_error(self, mock_blob_service_class):
        """Test case with Azure service error"""
        mock_blob_service_class.side_effect = AzureError("Generic Azure Error")

        response = self.client.get(self.url, {'blob_name': self.blob_name})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {
            'status': 'error',
            'message': 'Azure service error: Generic Azure Error'
        })

    def test_generic_azure_error_handling(self):
        """Test case for handling a generic Azure service error"""
        self.mock_container_client.get_blob_client.side_effect = AzureError(
            "Some Azure error occurred"
        )

        response = self.client.get(self.url, {'blob_name': self.blob_name})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {
            'status': 'error',
            'message': 'Azure service error: Some Azure error occurred'
        })

    def test_get_content_type(self):
        """Test case for checking content type based on blob name"""
        view = RetrieveImage()  # Create an instance of your view

        self.assertEqual(view.get_content_type('image.jpg'), 'image/jpeg')
        self.assertEqual(view.get_content_type('image.jpeg'), 'image/jpeg')
        self.assertEqual(view.get_content_type('image.png'), 'image/png')
        self.assertEqual(view.get_content_type('image.gif'), 'image/gif')
        self.assertEqual(view.get_content_type('image.txt'), 'application/octet-stream')

class TestRetrieveParamsView:
    """Tests RetrieveParams view"""

    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        """Setup method to initialize the API client"""
        self.url = reverse('retrieve_params')
        self.client = client

    def test_retrieve_params(self):
        """Test RetrieveParams view"""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['client_id'] == settings.CLIENT_ID
        assert response.data['tenant_id'] == settings.TENANT_ID
        assert response.data['status'] == status.HTTP_200_OK

@pytest.mark.django_db
class TestTranslateTextView:
    """Tests TranslateText view"""

    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        """Setup method to initialize the API client"""
        self.client = client
        self.url = reverse('translate-text')
        self.valid_payload = {
            'text': 'Hello, world!',
            'from': 'en',
            'to': ['fr', 'es']
        }
        self.invalid_payload_missing_to = {
            'text': 'Hello, world!',
            'from': 'en'
        }
        self.invalid_payload_invalid_to = {
            'text': 'Hello, world!',
            'from': 'en',
            'to': 'fr'
        }
        self.invalid_payload_missing_text = {
            'from': 'en',
            'to': ['fr', 'es']
        }

    @patch('requests.post')
    def test_translate_text_success(self, mock_post):
        """Test TranslateText view with valid payload"""
        mock_response = {
            'translations': [
                {'to': 'fr', 'text': 'Bonjour, le monde!'},
                {'to': 'es', 'text': '¡Hola, mundo!'}
            ]
        }
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = [mock_response]

        response = self.client.post(self.url, self.valid_payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'fr': 'Bonjour, le monde!',
            'es': '¡Hola, mundo!'
        }

    def test_translate_text_missing_to(self):
        """Test TranslateText view with missing 'to' parameter"""
        response = self.client.post(self.url, self.invalid_payload_missing_to, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'error': 'Invalid or missing "to" parameter'}

    def test_translate_text_invalid_to(self):
        """Test TranslateText view with invalid 'to' parameter"""
        response = self.client.post(self.url, self.invalid_payload_invalid_to, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'error': 'Invalid or missing "to" parameter'}

    def test_translate_text_missing_text(self):
        """Test TranslateText view with missing 'text' parameter"""
        response = self.client.post(self.url, self.invalid_payload_missing_text, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'error': 'Invalid or missing "text" parameter'}

    @patch('requests.post')
    def test_translate_text_request_exception(self, mock_post):
        """Test TranslateText view handling request exception"""
        mock_post.side_effect = RequestException("Request error")

        response = self.client.post(self.url, self.valid_payload, format='json')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {'error': 'Request error occurred: Request error'}

    @patch('api.views.TranslateText.translate_text')
    def test_translate_text_internal_error(self, mock_translate_text):
        """Test TranslateText view handling internal error"""
        mock_translate_text.side_effect = RequestException("Internal error")

        response = self.client.post(self.url, self.valid_payload, format='json')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {'error': 'Internal error'}
