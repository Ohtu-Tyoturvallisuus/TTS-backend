""" api/tests/unit/test_views.py """
# pylint: disable=attribute-defined-outside-init

from unittest.mock import patch, MagicMock
import io
import pytest
import jwt
from django.urls import reverse
from django.test import TestCase
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from azure.core.exceptions import AzureError, HttpResponseError, ResourceNotFoundError
from api.models import RiskNote
from api.views import RetrieveImage

pytestmark = pytest.mark.django_db

def test_api_root(client):
    """Test API root view"""
    response = client.get(reverse('api-root'))
    assert response.status_code == status.HTTP_200_OK
    assert 'projects_url' in response.context
    assert 'surveys_url' in response.context

class TestProjectListView:
    """Tests ProjectList view"""

    def setup_method(self):
        """Setup method"""
        self.url = reverse('project-list')
        self.project_data = {
            'project_id': 'test_project_id',
            'project_name': 'Test Project',
            'dimension_display_value': 'Test Dimension',
            'project_group': 'Test Group'
        }

    def test_project_list(self, client, create_project):
        """Test ProjectList view"""
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['project_id'] == create_project.project_id
        assert response.data[0]['project_name'] == create_project.project_name
        assert response.data[0]['dimension_display_value'] == create_project.dimension_display_value
        assert response.data[0]['project_group'] == create_project.project_group

    def test_project_create(self, client, create_user):
        """Test ProjectList view with POST request (non-admin user)"""
        client.force_authenticate(user=create_user)
        response = client.post(self.url, self.project_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    def test_project_create_admin(self, client, create_superuser):
        """Test ProjectList view with POST request (admin user)"""
        client.force_authenticate(user=create_superuser)
        response = client.post(self.url, self.project_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['project_id'] == 'test_project_id'
        assert response.data['project_name'] == 'Test Project'
        assert response.data['dimension_display_value'] == 'Test Dimension'
        assert response.data['project_group'] == 'Test Group'

class TestProjectDetailView:
    """Tests ProjectDetail view"""

    @pytest.fixture(autouse=True)
    def setup_method(self, create_project):
        """Setup method using create_project fixture"""
        self.project = create_project
        self.url = reverse('project-detail', kwargs={'pk': self.project.id})
        self.project_data = {
            'project_id': 'updated_project_id',
            'project_name': 'Updated Project',
            'dimension_display_value': 'Updated Dimension',
            'project_group': 'Updated Group'
        }

    def test_project_detail(self, client):
        """Test ProjectDetail view (allow any)"""
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['project_id'] == self.project.project_id
        assert response.data['project_name'] == self.project.project_name
        assert response.data['dimension_display_value'] == self.project.dimension_display_value
        assert response.data['project_group'] == self.project.project_group

    def test_project_detail_not_found(self, client):
        """Test ProjectDetail view with non-existing id"""
        response = client.get(reverse('project-detail', kwargs={'pk': 9999}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_project_update(self, client, create_superuser):
        """Test ProjectDetail view with PUT request (admin user)"""
        client.force_authenticate(user=create_superuser)
        response = client.put(self.url, self.project_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['project_id'] == 'updated_project_id'
        assert response.data['project_name'] == 'Updated Project'
        assert response.data['dimension_display_value'] == 'Updated Dimension'
        assert response.data['project_group'] == 'Updated Group'

    def test_project_delete(self, client, create_superuser):
        """Test ProjectDetail view with DELETE request (admin user)"""
        client.force_authenticate(user=create_superuser)
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None

class TestSurveyListView:
    """Tests SurveyList view"""

    @pytest.fixture(autouse=True)
    def setup_method(self, create_project, create_survey):
        """Setup method using create_project and create_survey fixtures"""
        self.project = create_project
        self.survey = create_survey
        self.survey_url = reverse('survey-list')
        self.project_url = reverse('survey-list', kwargs={'project_pk': self.project.id})
        self.survey_data = {
            'description': 'New Description',
            'task': 'New Task',
            'scaffold_type': 'New Scaffold'
        }

    def test_survey_list(self, client):
        """Test SurveyList view"""
        response = client.get(self.survey_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['description'] == self.survey.description
        assert response.data[0]['task'] == self.survey.task
        assert response.data[0]['scaffold_type'] == self.survey.scaffold_type

    def test_survey_list_for_project(self, client):
        """Test SurveyList view for a specific Project"""
        response = client.get(self.project_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['description'] == self.survey.description
        assert response.data[0]['task'] == self.survey.task
        assert response.data[0]['scaffold_type'] == self.survey.scaffold_type

    def test_create_survey_requires_project(self, client, create_user):
        """Test creating a Survey requires a Project"""
        client.force_authenticate(user=create_user)
        response = client.post(self.survey_url, self.survey_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'project' in response.data

        response = client.post(self.project_url, self.survey_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['project_name'] == self.project.project_name
        assert response.data['description'] == 'New Description'
        assert response.data['task'] == 'New Task'
        assert response.data['scaffold_type'] == 'New Scaffold'

class TestSurveyDetailView:
    """Tests SurveyDetail view"""

    @pytest.fixture(autouse=True)
    def setup_method(self, create_survey):
        """Setup method using create_survey fixture"""
        self.survey = create_survey
        self.url = reverse('survey-detail', kwargs={'pk': self.survey.id})
        self.survey_data = {
            'description': 'Updated Description',
            'task': 'Updated Task',
            'scaffold_type': 'Updated Scaffold'
        }

    def test_survey_detail(self, client):
        """Test SurveyDetail view"""
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['description'] == self.survey.description
        assert response.data['task'] == self.survey.task
        assert response.data['scaffold_type'] == self.survey.scaffold_type

    def test_survey_update(self, client, create_user):
        """Test SurveyDetail view with PUT request"""
        client.force_authenticate(user=create_user)
        response = client.put(self.url, self.survey_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['description'] == 'Updated Description'
        assert response.data['task'] == 'Updated Task'
        assert response.data['scaffold_type'] == 'Updated Scaffold'

    def test_survey_delete(self, client, create_user):
        """Test SurveyDetail view with DELETE request"""
        client.force_authenticate(user=create_user)
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None

class TestRiskNoteCreateView:
    """Tests RiskNoteCreate view"""

    @pytest.fixture(autouse=True)
    def setup_method(self, create_survey):
        """Setup method"""
        self.survey = create_survey
        self.valid_risknote_data = {
            'note': 'Test Risk Note',
            'description': 'Test Description',
            'status': 'Pending'
        }
        self.risknote = RiskNote.objects.create(
            survey=self.survey,
            note=self.valid_risknote_data['note'],
            description=self.valid_risknote_data['description'],
            status=self.valid_risknote_data['status']
        )
        self.url = reverse('risknote-create', kwargs={'survey_pk': self.survey.id})
        self.multiple_risknotes_data = [
            {
                'note': 'Test Risk Note 1',
                'description': 'Test Description 1',
                'status': 'Pending'
            },
            {
                'note': 'Test Risk Note 2',
                'description': 'Test Description 2',
                'status': 'Resolved'
            }
        ]

    def test_get_risk_notes_for_survey(self, client):
        """Test RiskNoteCreate view with GET request"""
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['note'] == self.risknote.note
        assert response.data[0]['description'] == self.risknote.description
        assert response.data[0]['status'] == self.risknote.status

    def test_post_single_risk_note(self, client):
        """Test RiskNoteCreate view with POST request for single RiskNote"""
        response = client.post(self.url, self.valid_risknote_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['note'] == 'Test Risk Note'
        assert response.data['description'] == 'Test Description'
        assert response.data['status'] == 'Pending'

    def test_post_multiple_risk_notes(self, client):
        """Test RiskNoteCreate view with POST request for multiple RiskNotes"""
        response = client.post(self.url, self.multiple_risknotes_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 2

        risknotes = RiskNote.objects.filter(survey=self.survey)
        assert risknotes.count() == 3
        assert risknotes[0].note == 'Test Risk Note'
        assert risknotes[0].description == 'Test Description'
        assert risknotes[0].status == 'Pending'
        assert risknotes[1].note == 'Test Risk Note 1'
        assert risknotes[1].description == 'Test Description 1'
        assert risknotes[1].status == 'Pending'
        assert risknotes[2].note == 'Test Risk Note 2'
        assert risknotes[2].description == 'Test Description 2'
        assert risknotes[2].status == 'Resolved'

class TestSignInView:
    """Tests SignIn view"""

    def setup_method(self):
        """Setup method"""
        self.url = reverse('signin')
        self.client = APIClient()

    def test_signin(self, client):
        """Test SignIn view with POST request"""
        data = {'username': 'testuser'}
        response = client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == "User 'testuser' created and signed in successfully"

    def test_signin_existing_user(self, client, create_user):
        """Test SignIn view with POST request for existing user"""
        user = create_user
        data = {'username': user.username}
        response = client.post(self.url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == f"User '{user.username}' signed in successfully"

    def test_signin_missing_username(self, client):
        """Test SignIn view with POST request for missing username"""
        response = client.post(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == "Username is required"

    def test_signin_guest_user(self):
        """Test SignIn view with POST request as guest user"""
        data = {'guest': True, 'username': 'guestuser'}
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == "User 'guestuser' created and signed in successfully"
        assert 'access_token' in response.data

        decoded_token = jwt.decode(
            response.data['access_token'],
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        assert decoded_token['username'] == 'guestuser'
        assert 'user_id' in decoded_token
        assert len(decoded_token['user_id']) == 64

class UploadImageTestCase(TestCase):
    """Tests UploadImage view"""

    def setup_method(self, client):
        """Setup method"""
        self.client = client
        self.url = '/api/upload-image/'

    def test_missing_image_file(self):
        """Test case where no image file is provided."""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'No image file provided.')

    def test_invalid_image_type(self):
        """Test case where an invalid file type is provided."""
        file = io.BytesIO(b"fake image data")
        file.name = 'test.txt'
        response = self.client.post(self.url, {'image': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid file type. Only images are allowed.')

    @patch('api.views.BlobServiceClient')
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
        self.assertIn('url', response.data)
        mock_blob_client.upload_blob.assert_called_once()

    @patch('api.views.BlobServiceClient')
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

    @patch('api.views.BlobServiceClient')
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

        self.blob_service_patcher = patch('api.views.BlobServiceClient')
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

    @patch('api.views.BlobServiceClient.get_container_client')
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

    @patch('api.views.BlobServiceClient')
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

    @patch('api.views.BlobServiceClient')
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
