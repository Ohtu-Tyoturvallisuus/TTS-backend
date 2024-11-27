""" api/tests/unit/test_models.py """

import pytest
from django.core.exceptions import ValidationError
from api.models import Project, Survey, RiskNote, Account

pytestmark = pytest.mark.django_db

def test_project_str():
    """Test Project model __str__ method"""
    project = Project(project_id='123', data_area_id='Area123',
                      project_name='Test project',
                      dimension_display_value='Value',
                      worker_responsible_personnel_number='Worker123',
                      customer_account='Customer123')
    assert str(project) == f'{project.project_name}'

def test_survey_str():
    """Test Survey model __str__ method"""
    project = Project(project_id='123', data_area_id='Area123',
                      project_name='Test project',
                      dimension_display_value='Value',
                      worker_responsible_personnel_number='Worker123',
                      customer_account='Customer123')
    survey = Survey(project=project, description='Test Description',
                    task=['Test Task'], scaffold_type=['Test Scaffold 1', 'Test Scaffold 2'])
    assert str(survey) == f'{", ".join(survey.task)} - {", ".join(survey.scaffold_type)}'

def test_risk_note_str():
    """Test RiskNote model __str__ method"""
    project = Project(project_id='123', data_area_id='Area123',
                      project_name='Test project',
                      dimension_display_value='Value',
                      worker_responsible_personnel_number='Worker123',
                      customer_account='Customer123')
    survey = Survey(project=project, description='Test Description',
                    task='Test Task', scaffold_type='Test Scaffold')
    risk_note = RiskNote(survey=survey, note='Test Risk Note')
    assert str(risk_note) == f'{risk_note.note} ({risk_note.created_at})'

def test_account_str():
    """Test Account model __str__ method"""
    account = Account(username='test_user')
    assert str(account) == f'{account.username} ({account.user_id})'

def test_survey_clean_valid_data():
    """Test Survey clean method with valid data"""
    project = Project(project_id='123', data_area_id='Area123',
                      project_name='Test project',
                      dimension_display_value='Value',
                      worker_responsible_personnel_number='Worker123',
                      customer_account='Customer123')
    project.save()
    survey = Survey(project=project, description='Test Description',
                    task=['Task 1'], scaffold_type=['Scaffold 1'])
    survey.clean()

def test_survey_clean_empty_task():
    """Test Survey clean method with empty task"""
    project = Project(project_id='123', data_area_id='Area123',
                      project_name='Test project',
                      dimension_display_value='Value',
                      worker_responsible_personnel_number='Worker123',
                      customer_account='Customer123')
    project.save()
    survey = Survey(project=project, description='Test Description',
                    task=[], scaffold_type=['Scaffold 1'])

    with pytest.raises(ValidationError) as excinfo:
        survey.clean()
    assert "Task field cannot be empty." in str(excinfo.value)

def test_survey_clean_empty_scaffold_type():
    """Test Survey clean method with empty scaffold_type"""
    project = Project(project_id='123', data_area_id='Area123',
                      project_name='Test project',
                      dimension_display_value='Value',
                      worker_responsible_personnel_number='Worker123',
                      customer_account='Customer123')
    project.save()
    survey = Survey(project=project, description='Test Description',
                    task=['Task 1'], scaffold_type=[])

    with pytest.raises(ValidationError) as excinfo:
        survey.clean()
    assert "Scaffolding type field cannot be empty." in str(excinfo.value)

def test_survey_clean_both_fields_empty():
    """Test Survey clean method with both task and scaffold_type empty"""
    project = Project(project_id='123', data_area_id='Area123',
                      project_name='Test project',
                      dimension_display_value='Value',
                      worker_responsible_personnel_number='Worker123',
                      customer_account='Customer123')
    project.save()
    survey = Survey(project=project, description='Test Description',
                    task=[], scaffold_type=[])

    with pytest.raises(ValidationError) as excinfo:
        survey.clean()
    assert "Task field cannot be empty." in str(excinfo.value)
    assert "Scaffolding type field cannot be empty." in str(excinfo.value)
