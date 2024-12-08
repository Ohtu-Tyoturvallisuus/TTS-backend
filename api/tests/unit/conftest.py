""" api/tests/unit/conftest.py """

from io import BytesIO
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from api.models import Project, Survey, RiskNote, Account

User = get_user_model()

@pytest.fixture(name='client')
def client_fixture():
    """Fixture to create an APIClient object"""
    return APIClient()

@pytest.fixture(name='create_project')
def create_project_fixture():
    """Fixture to create a Project object"""
    return Project.objects.create(
        project_id='test_project_id',
        data_area_id='test_data_area_id',
        project_name='Test Project',
        dimension_display_value='Test Dimension',
        worker_responsible_personnel_number='test_worker_number',
        customer_account='test_customer_account'
    )

@pytest.fixture(name='create_project_with_surveys')
def create_project_with_surveys(create_project):
    """Fixture to create a Project instance with multiple surveys"""
    project = create_project
    creator = Account.objects.create(
        user_id='creator_id_1',
        username="creatoruser1"
    )
    Survey.objects.bulk_create([
        Survey(
            project=project,
            creator=creator,
            description="Description 1",
            description_translations={},
            task=['Test Task'],
            scaffold_type=['Test Scaffold'],
            access_code='ABCDEF',
            is_completed=False,
            number_of_participants=0,
            language='en',
            translation_languages=[]
        ),
        Survey(
            project=project,
            creator=creator,
            description="Description 2",
            description_translations={},
            task=['Test Task 1', 'Test Task 2'],
            scaffold_type=['Test Scaffold 1', 'Test Scaffold 2'],
            access_code='AABCDE',
            is_completed=False,
            number_of_participants=0,
            language='en',
            translation_languages=[]
        )
    ])
    return project

@pytest.fixture(name='create_user')
def create_user_fixture():
    """Fixture to create a User object"""
    return User.objects.create(username='testuser', id='123')

@pytest.fixture(name='create_superuser')
def create_superuser_fixture():
    """Fixture to create a superuser"""
    return User.objects.create_superuser('admin')

@pytest.fixture(name='create_account')
def create_account_fixture():
    """Fixture to create an Account object"""
    return Account.objects.create(username='test_account', user_id='test_user_id')

@pytest.fixture(name='create_survey')
def create_survey_fixture(create_project):
    """Fixture to create a Survey object"""
    creator = Account.objects.create(
            user_id='creator_id',
            username="creatoruser"
        )
    survey = Survey(
        project=create_project,
        creator=creator,
        description='Test Description',
        task=['Test Task'],
        scaffold_type=['Test Scaffold'],
        access_code='AAABCD'
    )
    survey.full_clean()
    survey.save()
    return survey

@pytest.fixture(name='create_risk_note')
def create_risk_note_fixture(create_survey):
    """Fixture to create a RiskNote object"""
    return RiskNote.objects.create(survey=create_survey, note='Test Risk Note')

@pytest.fixture(name='mock_file')
def mock_file_fixture():
    """Fixture to mock a file object"""
    file = BytesIO(b"fake audio content")
    file.name = 'test_audio.mp3'
    file.content_type = 'audio/mpeg'
    return file
