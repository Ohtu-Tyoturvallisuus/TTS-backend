""" api/tests/unit/test_models.py """

from api.models import Project, Survey, RiskNote

def test_project_str():
    """Test Project model __str__ method"""
    project = Project(project_id='123', project_name='Test project',
                      dimension_display_value='Value', project_group='Group')
    assert str(project) == f'{project.project_name}'

def test_survey_str():
    """Test Survey model __str__ method"""
    project = Project(project_id='123', project_name='Test project',
                      dimension_display_value='Value', project_group='Group')
    survey = Survey(project=project, description='Test Description',
                    task='Test Task', scaffold_type='Test Scaffold')
    assert str(survey) == f'{survey.task} - {survey.scaffold_type}'

def test_risk_note_str():
    """Test RiskNote model __str__ method"""
    project = Project(project_id='123', project_name='Test project',
                      dimension_display_value='Value', project_group='Group')
    survey = Survey(project=project, description='Test Description',
                    task='Test Task', scaffold_type='Test Scaffold')
    risk_note = RiskNote(survey=survey, note='Test Risk Note')
    assert str(risk_note) == f'{risk_note.note} ({risk_note.created_at})'
