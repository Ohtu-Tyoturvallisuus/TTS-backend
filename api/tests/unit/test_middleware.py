""" api/tests/unit/test_middleware.py """
# pylint: disable=attribute-defined-outside-init

import json
from unittest.mock import patch
import pytest
import jwt
from django.http import JsonResponse
from django.test import RequestFactory
from django.conf import settings
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

    def test_invalid_token(self):
        """Test when an invalid token is provided"""
        request = self.factory.post('/some-url/', HTTP_AUTHORIZATION='Bearer invalid-token')

        with patch('jwt.decode', side_effect=jwt.InvalidTokenError):
            response = self.middleware(request)

        assert response.status_code == 401
        assert json.loads(response.content) == {'error': 'Invalid or expired token'}

    def test_expired_token(self):
        """Test when an expired token is provided"""
        request = self.factory.post('/some-url/', HTTP_AUTHORIZATION='Bearer expired-token')

        with patch('jwt.decode', side_effect=jwt.ExpiredSignatureError):
            response = self.middleware(request)

        assert response.status_code == 401
        assert json.loads(response.content) == {'error': 'Invalid or expired token'}

    def test_valid_token(self):
        """Test when a valid token is provided"""
        valid_token = jwt.encode({'some': 'payload'}, settings.SECRET_KEY, algorithm='HS256')
        request = self.factory.post('/some-url/', HTTP_AUTHORIZATION=f'Bearer {valid_token}')

        response = self.middleware(request)
        assert response.status_code == 200
        assert json.loads(response.content) == {'success': True}

    def test_signin_path(self):
        """Test that the middleware allows requests to the sign-in path without token validation"""
        request = self.factory.post('/api/signin/')
        response = self.middleware(request)

        assert response.status_code == 200
        assert json.loads(response.content) == {'success': True}
