""" api/tests/unit/test_serializers.py """

import pytest
import pytz
from django.test import RequestFactory
from django.urls import reverse
from api.serializers import (
    ProjectSerializer, ProjectListSerializer,
    SurveySerializer, SurveyNestedSerializer,
    RiskNoteSerializer, SignInSerializer)

pytestmark = pytest.mark.django_db

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

def test_project_list_serializer(create_project):
    """Test ProjectListSerializer for serialization"""
    project = create_project
    rf = RequestFactory()
    request = rf.get('/')
    serializer = ProjectListSerializer(project, context={'request': request})
    assert serializer.data == {
        'id': project.id,
        'url': request.build_absolute_uri(reverse('project-detail', kwargs={'pk': project.id})),
        'project_id': project.project_id,
        'project_name': project.project_name,
        'dimension_display_value': project.dimension_display_value,
        'project_group': project.project_group,
        'last_survey_date': None,
    }

def test_project_list_deserializer(create_project):
    """Test ProjectListSerializer for deserialization"""
    project = create_project
    data = {
        'project_id': 'new_project_id',
        'project_name': 'New Project',
        'dimension_display_value': 'New Dimension',
        'project_group': 'New Group'
    }
    serializer = ProjectListSerializer(project, data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == data

def test_project_list_serializer_get_last_survey_date(create_project_with_surveys):
    """Test ProjectListSerializer's get_last_survey_date method"""
    project = create_project_with_surveys
    last_survey = project.surveys.order_by('-created_at').first()
    last_survey_created_at = last_survey.created_at.isoformat() if last_survey else None
    if last_survey_created_at:
        last_survey_created_at = last_survey_created_at.replace('T', ' ')
    rf = RequestFactory()
    request = rf.get('/')

    serializer = ProjectListSerializer(project, context={'request': request})
    last_survey_date_from_serializer = str(serializer.data['last_survey_date'])

    assert last_survey_date_from_serializer == last_survey_created_at

def test_survey_serializer(create_survey):
    """Test SurveySerializer for serialization"""
    survey = create_survey
    serializer = SurveySerializer(survey)
    local_tz = pytz.timezone('Europe/Helsinki')
    created_at_local = survey.created_at.astimezone(local_tz).isoformat()
    assert serializer.data == {
        'id': survey.id,
        'project_name': survey.project.project_name,
        'description': survey.description,
        'task': survey.task,
        'scaffold_type': survey.scaffold_type,
        'created_at': created_at_local,
        'risk_notes': [],
    }

def test_survey_deserializer(create_survey):
    """Test SurveySerializer for deserialization"""
    survey = create_survey
    data = {
        'project': survey.project.id,
        'description': 'New Description',
        'task': 'New Task',
        'scaffold_type': 'New Scaffold',
    }
    serializer = SurveySerializer(survey, data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'description': 'New Description',
        'task': 'New Task',
        'scaffold_type': 'New Scaffold',
    }

def test_survey_nested_serializer(create_survey):
    """Test SurveyNestedSerializer for serialization"""
    survey = create_survey
    project_id = survey.project.id
    rf = RequestFactory()
    request = rf.get('/')
    serializer = SurveyNestedSerializer(survey, context={'request': request})
    local_tz = pytz.timezone('Europe/Helsinki')
    created_at_local = survey.created_at.astimezone(local_tz).isoformat()
    assert serializer.data == {
        'id': survey.id,
        'url': request.build_absolute_uri(reverse(
            'survey-detail', kwargs={'project_pk': project_id, 'pk': survey.id}
            )),
        'task': survey.task,
        'scaffold_type': survey.scaffold_type,
        'created_at': created_at_local,
    }

def test_survey_nested_deserializer(create_survey):
    """Test SurveyNestedSerializer for deserialization"""
    survey = create_survey
    data = {
        'description': 'New Description',
        'task': 'New Task',
        'scaffold_type': 'New Scaffold',
    }
    serializer = SurveyNestedSerializer(survey, data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'task': 'New Task',
        'scaffold_type': 'New Scaffold',
    }

def test_survey_nested_serializer_get_url(create_survey, rf):
    """Test SurveyNestedSerializer's get_url method"""
    survey = create_survey
    rf = RequestFactory()
    request = rf.get('/')
    serializer_context = {'request': request}
    serializer = SurveyNestedSerializer(survey, context=serializer_context)
    expected_url = request.build_absolute_uri(
        reverse('survey-detail', kwargs={'project_pk': survey.project.id, 'pk': survey.id})
    )
    assert serializer.data['url'] == expected_url

def test_risk_note_serializer(create_risk_note):
    """Test RiskNoteSerializer for serialization"""
    risk_note = create_risk_note
    serializer = RiskNoteSerializer(risk_note)
    local_tz = pytz.timezone('Europe/Helsinki')
    created_at_local = risk_note.created_at.astimezone(local_tz).isoformat()
    assert serializer.data == {
        'id': risk_note.id,
        'survey_id': risk_note.survey.id,
        'note': risk_note.note,
        'description': '',
        'status': '',
        'risk_type': '',
        'images': [],
        'created_at': created_at_local,
    }

def test_risk_note_deserializer(create_risk_note):
    """Test RiskNoteSerializer for deserialization"""
    risk_note = create_risk_note
    data = {
        'survey_id': risk_note.survey.id,
        'note': 'New Risk Note',
        'description': 'Updated Description',
        'status': 'Updated Status',
        'risk_type': 'Updated Risk Type',
        'images': ['image1', 'image2'],
    }
    serializer = RiskNoteSerializer(risk_note, data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == {
        'note': 'New Risk Note',
        'description': 'Updated Description',
        'status': 'Updated Status',
        'risk_type': 'Updated Risk Type',
        'images': ['image1', 'image2'],
    }

def test_signin_serializer():
    """Test SignInSerializer for serialization"""
    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    serializer = SignInSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == {'username': 'testuser'}
    assert serializer.data == {'username': 'testuser'}

def test_signin_deserializer():
    """Test SignInSerializer for deserialization"""
    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    serializer = SignInSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == {'username': 'testuser'}
    assert serializer.data == {'username': 'testuser'}
