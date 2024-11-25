""" api/tests/unit/views/test.survey_views.py """
# pylint: disable=attribute-defined-outside-init

import json
from unittest.mock import patch
import jwt
import pytest
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from api.models import AccountSurvey, Survey, Project, Account

pytestmark = pytest.mark.django_db

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
            'task': ['New Task'],
            'scaffold_type': ['New Scaffold']
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

    def test_create_survey_requires_project(self, client, create_account):
        """Test creating a Survey requires a Project"""
        client.force_authenticate(user=create_account)

        token_payload = {
            "username": create_account.username,
            "user_id": create_account.user_id
        }
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm="HS256")
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = client.post(
            self.survey_url,
            data=json.dumps(self.survey_data),
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'project' in response.data

        response = client.post(
            self.project_url,
            data=json.dumps(self.survey_data),
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['project_name'] == self.project.project_name
        assert response.data['description'] == 'New Description'
        assert response.data['task'] == ['New Task']
        assert response.data['scaffold_type'] == ['New Scaffold']

    def test_missing_authorization_header(self, client):
        """Test SurveyList view with missing Authorization header"""
        response = client.post(
            self.project_url,
            data=json.dumps(self.survey_data),
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert response.data['error'] == "Authorization header is required"

    def test_invalid_authorization_header_format(self, client):
        """Test SurveyList view with invalid Authorization header format"""
        client.credentials(HTTP_AUTHORIZATION="InvalidHeader")
        response = client.post(
            self.project_url,
            data=json.dumps(self.survey_data),
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert response.data['error'] == "Authorization header is required"

    def test_expired_token(self, client, create_account):
        """Test SurveyList view with expired JWT token"""
        client.force_authenticate(user=create_account)

        token_payload = {
            "username": create_account.username,
            "user_id": create_account.user_id,
            "exp": 0  # Immediate expiration
        }
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm="HS256")
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = client.post(
            self.project_url,
            data=json.dumps(self.survey_data),
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert response.data['error'] == "Token has expired"

    def test_invalid_token(self, client, create_account):
        """Test SurveyList view with an invalid JWT token"""
        client.force_authenticate(user=create_account)

        # Invalid token with malformed payload
        invalid_token = "Bearer invalid.token.payload"
        client.credentials(HTTP_AUTHORIZATION=f"{invalid_token}")

        response = client.post(
            self.project_url,
            data=json.dumps(self.survey_data),
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert response.data['error'] == "Invalid token"


class TestSurveyDetailView:
    """Tests SurveyDetail view"""

    @pytest.fixture(autouse=True)
    def setup_method(self, create_survey):
        """Setup method using create_survey fixture"""
        self.survey = create_survey
        self.url = reverse('survey-detail', kwargs={'pk': self.survey.id})
        self.survey_data = {
            'description': 'Updated Description',
            'task': ['Updated Task'],
            'scaffold_type': ['Updated Scaffold']
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
        response = client.put(
            self.url,
            data=json.dumps(self.survey_data),
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['description'] == 'Updated Description'
        assert response.data['task'] == ['Updated Task']
        assert response.data['scaffold_type'] == ['Updated Scaffold']

    def test_survey_delete(self, client, create_user):
        """Test SurveyDetail view with DELETE request"""
        client.force_authenticate(user=create_user)
        response = client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None

class TestFilledSurveysView:
    """Tests for the FilledSurveys view"""

    @pytest.fixture(autouse=True)
    def setup_method(self, create_account, create_survey):
        """Setup method for creating test data"""
        self.account = create_account
        self.survey = create_survey
        self.project = self.survey.project
        self.url = reverse('filled-surveys')

        AccountSurvey.objects.create(account=self.account, survey=self.survey)

    def test_filled_surveys_success(self, client):
        """Test successfully retrieving filled surveys"""
        token_payload = {
            "username": self.account.username,
            "user_id": self.account.user_id
        }
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm="HS256")

        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert 'filled_surveys' in response.data
        assert len(response.data['filled_surveys']) == 1
        filled_survey = response.data['filled_surveys'][0]
        assert filled_survey['id'] == self.survey.id
        assert filled_survey['project_id'] == self.project.project_id
        assert filled_survey['project_name'] == self.project.project_name

    def test_missing_authorization_header(self, client):
        """Test request with missing Authorization header"""
        response = client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['error'] == "Authorization header is required"


    def test_expired_token(self, client):
        """Test request with an expired token"""
        token_payload = {
            "username": self.account.username,
            "user_id": self.account.user_id,
            "exp": 0
        }
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm="HS256")

        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['error'] == "Token has expired"

    def test_invalid_token(self, client):
        """Test request with an invalid token"""
        client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.payload")

        response = client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['error'] == "Invalid token"

    def test_account_not_found(self, client):
        """Test request with a token for a non-existent account"""
        token_payload = {
            "username": "nonexistent_user",
            "user_id": "nonexistent_id"
        }
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm="HS256")

        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['error'] == "Account not found"

@pytest.mark.django_db
class TestJoinSurveyView:
    """Tests for the JoinSurvey view"""
    def setup_method(self):
        """Setup method for JoinSurvey tests"""
        self.client = APIClient()
        self.project = Project.objects.create(
            project_id='123',
            data_area_id='Area123',
            project_name='Test project',
            dimension_display_value='Value',
            worker_responsible_personnel_number='Worker123',
            customer_account='Customer123'
        )
        self.survey = Survey.objects.create(
            project=self.project,
            description='Test Description',
            task=['Task 1'],
            scaffold_type=['Scaffold 1'],
            access_code='ABC123'
        )
        self.account = Account.objects.create(
            user_id=1,
            username="testuser"
        )
        self.token = jwt.encode(
            {"user_id": self.account.user_id},
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        self.auth_header = f"Bearer {self.token}"

    def test_join_survey_successful(self):
        """Test successfully joining a survey"""
        response = self.client.post(
            reverse('join-survey', args=[self.survey.access_code]),
            HTTP_AUTHORIZATION=self.auth_header
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == {"detail": "The user has successfully joined the survey."}
        assert AccountSurvey.objects.filter(account=self.account, survey=self.survey).exists()

    def test_join_survey_already_joined(self):
        """Test trying to join a survey that the user already joined"""
        AccountSurvey.objects.create(account=self.account, survey=self.survey)

        response = self.client.post(
            reverse('join-survey', args=[self.survey.access_code]),
            HTTP_AUTHORIZATION=self.auth_header
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "The user has already joined this survey."}

    def test_join_survey_invalid_access_code(self):
        """Test joining a survey with an invalid access code"""
        response = self.client.post(
            reverse('join-survey', args=['INVALID']),
            HTTP_AUTHORIZATION=self.auth_header
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_join_survey_missing_authorization_header(self):
        """Test joining a survey without an Authorization header"""
        response = self.client.post(
            reverse('join-survey', args=[self.survey.access_code])
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"error": "Authorization header is required."}

    def test_join_survey_invalid_token(self):
        """Test joining a survey with an invalid token"""
        response = self.client.post(
            reverse('join-survey', args=[self.survey.access_code]),
            HTTP_AUTHORIZATION="Bearer invalidtoken"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == {"error": "Invalid token."}

    def test_join_survey_expired_token(self):
        """Test joining a survey with an expired token"""
        with patch('jwt.decode', side_effect=jwt.ExpiredSignatureError):
            response = APIClient().post(
                reverse('join-survey', args=['ABC123']),
                HTTP_AUTHORIZATION="Bearer sometoken"
            )
            assert response.status_code == 401
            assert response.data == {"error": "Token has expired."}
