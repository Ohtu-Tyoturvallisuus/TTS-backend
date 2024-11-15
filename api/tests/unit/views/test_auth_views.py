""" api/tests/unit/views/test.auth_views.py """
# pylint: disable=attribute-defined-outside-init

import jwt
import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

class TestSignInView:
    """Tests SignIn view"""

    def setup_method(self):
        """Setup method"""
        self.url = reverse('signin')
    def test_signin(self, client):
        """Test SignIn view with POST request"""
        data = {'username': 'testuser'}
        response = client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == "User 'testuser' created and signed in successfully"

    def test_signin_existing_user(self, client, create_user):
        """Test SignIn view with POST request for existing user"""
        user = create_user
        data = {'username': user.username}
        response = client.post(self.url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == f"User '{user.username}' signed in successfully"

    def test_signin_missing_username(self, client):
        """Test SignIn view with POST request for missing username"""
        response = client.post(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == "Username is required"

    def test_signin_guest_user(self, client):
        """Test SignIn view with POST request as guest user"""
        data = {'guest': True, 'username': 'guestuser'}
        response = client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == "User 'guestuser' created and signed in successfully"
        assert 'access_token' in response.data

        decoded_token = jwt.decode(
            response.data['access_token'],
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        assert decoded_token['username'] == 'guestuser'
        assert 'user_id' in decoded_token
        assert len(decoded_token['user_id']) == 64
