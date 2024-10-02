""" api/tests/unit/test_serializers.py """
import pytest
import pytz
from django.contrib.auth import get_user_model
from api.serializers import ProjectSerializer, SurveySerializer, RiskNoteSerializer
from api.models import Project, Survey, RiskNote

User = get_user_model()

pytestmark = pytest.mark.django_db

@pytest.fixture(name='create_project')
def create_project_fixture():
    """Fixture to create a Project object"""
    return Project.objects.create(
        project_id='test_project_id',
        project_name='Test Project',
        dimension_display_value='Test Dimension',
        project_group='Test Group'
    )

@pytest.fixture(name='create_user')
def create_user_fixture():
    """Fixture to create a User object"""
    return User.objects.create(username='testuser')

@pytest.fixture(name='create_survey')
def create_survey_fixture(create_project, create_user):
    """Fixture to create a Survey object"""
    return Survey.objects.create(
        project=create_project,
        title='Test Survey',
        description='Test Description'
    )

@pytest.fixture(name='create_risk_note')
def create_risk_note_fixture(create_survey):
    """Fixture to create a RiskNote object"""
    return RiskNote.objects.create(survey=create_survey, note='Test Risk Note')


def test_project_serializer(create_project):
    """Test ProjectSerializer for serialization"""
    project = create_project
    serializer = ProjectSerializer(project)
    assert serializer.data == {
        'id': project.id,
        'project_id': project.project_id,
        'project_name': project.project_name,
        'dimension_display_value': project.dimension_display_value,
        'project_group': project.project_group,
        'surveys': []
    }

def test_project_deserializer(create_project):
    """Test ProjectSerializer for deserialization"""
    project = create_project
    data = {
        'project_id': 'new_project_id',
        'project_name': 'New Project',
        'dimension_display_value': 'New Dimension',
        'project_group': 'New Group'
    }
    serializer = ProjectSerializer(project, data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == data

def test_survey_serializer(create_survey):
    """Test SurveySerializer for serialization"""
    survey = create_survey
    serializer = SurveySerializer(survey)
    local_tz = pytz.timezone('Europe/Helsinki')
    created_at_local = survey.created_at.astimezone(local_tz).isoformat()
    assert serializer.data == {
        'id': survey.id,
        'project': survey.project.project_name,
        'title': survey.title,
        'description': survey.description,
        'created_at': created_at_local,
        'risk_notes': [],
    }

def test_survey_deserializer(create_survey):
    """Test SurveySerializer for deserialization"""
    survey = create_survey
    data = {
        'project': survey.project.id,
        'title': 'New Survey',
        'description': 'New Description',
    }
    serializer = SurveySerializer(survey, data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'title': 'New Survey',
        'description': 'New Description',
    }

def test_risk_note_serializer(create_risk_note):
    """Test RiskNoteSerializer for serialization"""
    risk_note = create_risk_note
    serializer = RiskNoteSerializer(risk_note)
    local_tz = pytz.timezone('Europe/Helsinki')
    created_at_local = risk_note.created_at.astimezone(local_tz).isoformat()
    assert serializer.data == {
        'id': risk_note.id,
        'survey': risk_note.survey.title,
        'note': risk_note.note,
        'description': '',
        'status': '',
        'created_at': created_at_local,
    }

def test_risk_note_deserializer(create_risk_note):
    """Test RiskNoteSerializer for deserialization"""
    risk_note = create_risk_note
    data = {
        'survey': risk_note.survey.id,
        'note': 'New Risk Note',
        'description': 'Updated Description',
        'status': 'Updated Status'
    }
    serializer = RiskNoteSerializer(risk_note, data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'note': 'New Risk Note',
        'description': 'Updated Description',
        'status': 'Updated Status'
    }

# def test_risk_note_creation(create_survey):
#     """Test RiskNoteSerializer for creation of a new RiskNote"""
#     data = {
#         'note': 'New Risk Note',
#         'description': 'New Description',
#         'status': 'Pending'
#     }
#     serializer = RiskNoteSerializer(data=data, context={'survey': create_survey})
#     assert serializer.is_valid()
#     risk_note = serializer.save()
#     assert risk_note.note == data['note']
#     assert risk_note.description == data['description']
#     assert risk_note.status == data['status']
#     assert risk_note.survey == create_survey

def test_risk_note_update(create_risk_note):
    """Test RiskNoteSerializer for updating an existing RiskNote"""
    risk_note = create_risk_note
    data = {
        'note': 'Updated Risk Note',
        'description': 'Updated Description',
        'status': 'Closed'
    }
    serializer = RiskNoteSerializer(risk_note, data=data, partial=True)
    assert serializer.is_valid()
    updated_risk_note = serializer.save()
    assert updated_risk_note.note == data['note']
    assert updated_risk_note.description == data['description']
    assert updated_risk_note.status == data['status']
