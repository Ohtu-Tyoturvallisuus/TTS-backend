""" api/tests/unit/views/test.risknote_views.py """
# pylint: disable=attribute-defined-outside-init

import pytest
from django.urls import reverse
from rest_framework import status

from api.models import RiskNote

pytestmark = pytest.mark.django_db

class TestRiskNoteCreateView:
    """Tests RiskNoteCreate view"""

    @pytest.fixture(autouse=True)
    def setup_method(self, create_survey):
        """Setup method"""
        self.survey = create_survey
        self.valid_risknote_data = {
            'note': 'Test Risk Note',
            'description': 'Test Description',
            'status': 'Pending'
        }
        self.risknote = RiskNote.objects.create(
            survey=self.survey,
            note=self.valid_risknote_data['note'],
            description=self.valid_risknote_data['description'],
            status=self.valid_risknote_data['status']
        )
        self.url = reverse('risknote-create', kwargs={'survey_pk': self.survey.id})
        self.multiple_risknotes_data = [
            {
                'note': 'Test Risk Note 1',
                'description': 'Test Description 1',
                'status': 'Pending'
            },
            {
                'note': 'Test Risk Note 2',
                'description': 'Test Description 2',
                'status': 'Resolved'
            }
        ]

    def test_get_risk_notes_for_survey(self, client):
        """Test RiskNoteCreate view with GET request"""
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['note'] == self.risknote.note
        assert response.data[0]['description'] == self.risknote.description
        assert response.data[0]['status'] == self.risknote.status

    def test_post_single_risk_note(self, client):
        """Test RiskNoteCreate view with POST request for single RiskNote"""
        response = client.post(self.url, self.valid_risknote_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['note'] == 'Test Risk Note'
        assert response.data['description'] == 'Test Description'
        assert response.data['status'] == 'Pending'

    def test_post_multiple_risk_notes(self, client):
        """Test RiskNoteCreate view with POST request for multiple RiskNotes"""
        response = client.post(self.url, self.multiple_risknotes_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 2

        risknotes = RiskNote.objects.filter(survey=self.survey)
        assert risknotes.count() == 3
        assert risknotes[0].note == 'Test Risk Note'
        assert risknotes[0].description == 'Test Description'
        assert risknotes[0].status == 'Pending'
        assert risknotes[1].note == 'Test Risk Note 1'
        assert risknotes[1].description == 'Test Description 1'
        assert risknotes[1].status == 'Pending'
        assert risknotes[2].note == 'Test Risk Note 2'
        assert risknotes[2].description == 'Test Description 2'
        assert risknotes[2].status == 'Resolved'
