""" api/tests/unit/test_models.py """

from unittest.mock import patch
import pytest
from django.core.exceptions import ValidationError
from api.models import Project, Survey, RiskNote, Account, generate_access_code

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

def test_generate_access_code():
    """Test generate_access_code creates valid codes"""
    access_code = generate_access_code()
    assert len(access_code) == 6
    assert access_code.isalnum()
    assert '0' not in access_code and 'O' not in access_code

def test_generate_access_code_handles_duplicates():
    """Test generate_access_code retries on duplicates"""
    project = Project(project_id='123', data_area_id='Area123',
                     project_name='Test project',
                     dimension_display_value='Value',
                     worker_responsible_personnel_number='Worker123',
                     customer_account='Customer123')
    project.save()

    existing_survey = Survey(project=project, description='Existing Survey',
                           task=['Task'], scaffold_type=['Scaffold'])
    existing_survey.save()

    # Mock random.choices to first return existing code, then new one
    with patch('random.choices',
              side_effect=[list(existing_survey.access_code), ['A', 'B', 'C', '1', '2', '3']]):
        access_code = generate_access_code()
        assert access_code == 'ABC123'
        assert access_code != existing_survey.access_code

def test_survey_save_calls_clean():
    """Test Survey save method calls clean"""
    project = Project(project_id='123', data_area_id='Area123',
                      project_name='Test project',
                      dimension_display_value='Value',
                      worker_responsible_personnel_number='Worker123',
                      customer_account='Customer123')
    project.save()

    survey = Survey(project=project, description='Test Description',
                    task=['Task'], scaffold_type=['Scaffold'])

    with patch.object(Survey, 'clean', wraps=survey.clean) as mock_clean:
        survey.save()
        mock_clean.assert_called_once()
