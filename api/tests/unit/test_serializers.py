""" api/tests/unit/test_serializers.py """
import pytest
import pytz
from django.contrib.auth import get_user_model
from api.serializers import WorksiteSerializer, SurveySerializer, RiskNoteSerializer
from api.models import Worksite, Survey, RiskNote

User = get_user_model()

pytestmark = pytest.mark.django_db

@pytest.fixture(name='create_worksite')
def create_worksite_fixture():
    """Fixture to create a Worksite object"""
    return Worksite.objects.create(name='Test Worksite', location='Test Location')

@pytest.fixture(name='create_user')
def create_user_fixture():
    """Fixture to create a User object"""
    return User.objects.create(username='testuser')

@pytest.fixture(name='create_survey')
def create_survey_fixture(create_worksite, create_user):
    """Fixture to create a Survey object"""
    return Survey.objects.create(
        worksite=create_worksite,
        overseer=create_user,
        title='Test Survey',
        description='Test Description'
    )

@pytest.fixture(name='create_risk_note')
def create_risk_note_fixture(create_survey):
    """Fixture to create a RiskNote object"""
    return RiskNote.objects.create(survey=create_survey, note='Test Risk Note')


def test_worksite_serializer(create_worksite):
    """Test WorksiteSerializer for serialization"""
    worksite = create_worksite
    serializer = WorksiteSerializer(worksite)
    assert serializer.data == {
        'id': worksite.id,
        'name': worksite.name,
        'location': worksite.location,
        'surveys': []
    }

def test_worksite_deserializer(create_worksite):
    """Test WorksiteSerializer for deserialization"""
    worksite = create_worksite
    data = {
        'name': 'New Worksite',
        'location': 'New Location'
    }
    serializer = WorksiteSerializer(worksite, data=data)
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
        'worksite': survey.worksite.name,
        'overseer': survey.overseer.username,
        'title': survey.title,
        'description': survey.description,
        'created_at': created_at_local,
        'risk_notes': []
    }

def test_survey_deserializer(create_survey):
    """Test SurveySerializer for deserialization"""
    survey = create_survey
    data = {
        'worksite': survey.worksite.id,
        'overseer': survey.overseer.id,
        'title': 'New Survey',
        'description': 'New Description'
    }
    serializer = SurveySerializer(survey, data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'title': 'New Survey',
        'description': 'New Description'
    }

def test_risk_note_serializer(create_risk_note):
    """Test RiskNoteSerializer for serialization"""
    risk_note = create_risk_note
    serializer = RiskNoteSerializer(risk_note)
    local_tz = pytz.timezone('Europe/Helsinki')
    created_at_local = risk_note.created_at.astimezone(local_tz).isoformat()
    assert serializer.data == {
        'id': risk_note.id,
        'note': risk_note.note,
        'created_at': created_at_local,
        'description': '',
        'status': ''
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

def test_risk_note_creation(create_survey):
    """Test RiskNoteSerializer for creation of a new RiskNote"""
    data = {
        'note': 'New Risk Note',
        'description': 'New Description',
        'status': 'Pending'
    }
    serializer = RiskNoteSerializer(data=data, context={'survey': create_survey})
    assert serializer.is_valid()
    risk_note = serializer.save()
    assert risk_note.note == data['note']
    assert risk_note.description == data['description']
    assert risk_note.status == data['status']
    assert risk_note.survey == create_survey

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
