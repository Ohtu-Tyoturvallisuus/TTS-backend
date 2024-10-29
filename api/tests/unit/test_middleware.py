""" api/tests/unit/test_middleware.py """
# pylint: disable=attribute-defined-outside-init

import json
from unittest.mock import patch
import pytest
from django.http import JsonResponse
from django.test import RequestFactory
from api.middleware.access_token_middleware import AccessTokenMiddleware

@pytest.mark.django_db
class TestAccessTokenMiddleware:
    """Tests for AccessTokenMiddleware"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup method to initialize RequestFactory and the middleware"""
        self.factory = RequestFactory()
        self.middleware = AccessTokenMiddleware(
            get_response=lambda request: JsonResponse({'success': True})
        )

    def test_missing_token(self):
        """Test when no token is provided"""
        request = self.factory.post('/some-url/')
        response = self.middleware(request)
        assert response.status_code == 401

        assert json.loads(response.content) == {
            'error': 'Authentication credentials were not provided'
        }

    @patch('api.middleware.access_token_middleware.requests.get')
    def test_invalid_token(self, mock_get):
        """Test when an invalid token is provided"""
        request = self.factory.post('/some-url/', HTTP_AUTHORIZATION='Bearer invalid-token')
        mock_get.return_value.status_code = 401
        response = self.middleware(request)
        assert response.status_code == 401

        assert json.loads(response.content) == {'error': 'Invalid or expired token'}

    @patch('api.middleware.access_token_middleware.requests.get')
    def test_valid_token(self, mock_get):
        """Test when a valid token is provided"""
        request = self.factory.post('/some-url/', HTTP_AUTHORIZATION='Bearer valid-token')
        mock_get.return_value.status_code = 200
        response = self.middleware(request)
        assert response.status_code == 200

        assert json.loads(response.content) == {'success': True}
