""" api/tests/unit/test_models.py """

from api.models import Project, Survey, RiskNote

def test_project_str():
    """Test project model __str__ method"""
    project = Project(project_id='123', project_name='Test project', dimension_display_value='Value', project_group='Group')
    assert str(project) == 'Test project'

def test_survey_str():
    """Test Survey model __str__ method"""
    project = Project(project_id='123', project_name='Test project', dimension_display_value='Value', project_group='Group')
    survey = Survey(project=project, title='Test Survey', description='Test Description')
    assert str(survey) == 'Test Survey'

def test_risk_note_str():
    """Test RiskNote model __str__ method"""
    project = Project(project_id='123', project_name='Test project', dimension_display_value='Value', project_group='Group')
    survey = Survey(project=project, title='Test Survey', description='Test Description')
    risk_note = RiskNote(survey=survey, note='Test Risk Note')
    assert str(risk_note) == f'Test Risk Note ({risk_note.created_at})'
