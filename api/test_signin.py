from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

class SignInViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/signin/'

    def test_signin_with_new_user(self):
        data = {'username': 'newuser'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User created and signed in successfully')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signin_with_existing_user(self):
        existing_user = User.objects.create(username='existinguser')
        data = {'username': 'existinguser'}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User signed in successfully')
        self.assertEqual(User.objects.filter(username='existinguser').count(), 1)

    def test_signin_without_username(self):
        data = {}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Username is required')
