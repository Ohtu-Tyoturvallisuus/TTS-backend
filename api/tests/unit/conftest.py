""" api/tests/unit/conftest.py """
from unittest import mock
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from api.models import Project, Survey, RiskNote

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
        project_name='Test Project',
        dimension_display_value='Test Dimension',
        project_group='Test Group'
    )

@pytest.fixture(name='create_project_with_surveys')
def create_project_with_surveys(create_project):
    """Fixture to create a Project instance with multiple surveys"""
    project = create_project
    Survey.objects.bulk_create([
        Survey(
            project=project,
            description="Description 1",
            task='Test Task 1',
            scaffold_type='Test Scaffold 1'),
        Survey(
            project=project,
            description="Description 2",
            task='Test Task 2',
            scaffold_type='Test Scaffold 2')
    ])
    return project

@pytest.fixture(name='create_user')
def create_user_fixture():
    """Fixture to create a User object"""
    return User.objects.create(username='testuser')

@pytest.fixture(name='create_superuser')
def create_superuser_fixture():
    """Fixture to create a superuser"""
    return User.objects.create_superuser('admin')

@pytest.fixture(name='create_survey')
def create_survey_fixture(create_project):
    """Fixture to create a Survey object"""
    return Survey.objects.create(
        project=create_project,
        description='Test Description',
        task='Test Task',
        scaffold_type='Test Scaffold'
    )

@pytest.fixture(name='create_risk_note')
def create_risk_note_fixture(create_survey):
    """Fixture to create a RiskNote object"""
    return RiskNote.objects.create(survey=create_survey, note='Test Risk Note')

@pytest.fixture(name='mock_file')
def mock_file_fixture():
    """Fixture to mock a file object"""
    file = mock.MagicMock(spec=['name', 'chunks'])
    file.name = 'test_file.mp3'
    file.chunks.return_value = [b'testchunk']
    return file
