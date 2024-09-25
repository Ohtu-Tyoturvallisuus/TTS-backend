""" api/tests/unit/test_models.py """

from api.models import Worksite, Survey, RiskNote

def test_worksite_str():
    """Test Worksite model __str__ method"""
    worksite = Worksite(name='Test Worksite', location='Test Location')
    assert str(worksite) == 'Test Worksite'

def test_survey_str():
    """Test Survey model __str__ method"""
    worksite = Worksite(name='Test Worksite', location='Test Location')
    survey = Survey(worksite=worksite, title='Test Survey', description='Test Description')
    assert str(survey) == 'Test Survey'

def test_risk_note_str():
    """Test RiskNote model __str__ method"""
    worksite = Worksite(name='Test Worksite', location='Test Location')
    survey = Survey(worksite=worksite, title='Test Survey', description='Test Description')
    risk_note = RiskNote(survey=survey, note='Test Risk Note')
    assert str(risk_note) == f'Test Risk Note ({risk_note.created_at})'
